from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from PIL import Image, ImageFilter, ImageStat

from .catalog import FloraSpecies, load_catalog
from .config import Settings, get_settings
from .safety import (
    CONSUMPTION_WARNING,
    REQUIRED_DISCLAIMER,
    confidence_status,
    low_confidence_message,
)


class ModelUnavailableError(RuntimeError):
    """Raised when optional CLIP dependencies cannot be loaded."""


@dataclass(frozen=True)
class SpeciesScore:
    species: FloraSpecies
    score: float


@dataclass(frozen=True)
class FloraGateResult:
    is_flora: bool
    flora_probability: float
    top_prompt: str
    method: str


FLORA_GATE_PROMPTS = [
    "a close-up photo of a leaf",
    "a close-up photo of a flower",
    "a photo of a tree or woody plant",
    "a photo of a mushroom or fungus",
    "a photo of moss, grass, or groundcover",
    "a photo of a cactus or succulent",
    "a photo of fruit, seeds, cones, or berries growing from a plant",
    "a photo of an aquatic plant",
]

NON_FLORA_GATE_PROMPTS = [
    "a photo of a person",
    "a photo of an animal",
    "a photo of a vehicle",
    "a photo of a building or room",
    "a screenshot, document, chart, or user interface",
    "a photo of a household object",
    "a plate of prepared food",
    "an abstract image with no plant, fungus, moss, leaf, flower, seed, or tree",
]

NON_FLORA_REJECTION_MESSAGE = (
    "Only flora images are allowed. Non-flora images, including people, animals, "
    "vehicles, buildings, screenshots, prepared food, and household objects, are not allowed."
)


class FloraIdentifier:
    def __init__(self, settings: Settings | None = None, species: list[FloraSpecies] | None = None):
        self.settings = settings or get_settings()
        self.species = species or load_catalog(self.settings.catalog_path)
        self._clip_model: Any | None = None
        self._clip_processor: Any | None = None
        self._torch: Any | None = None

    def identify(self, image: Image.Image) -> dict[str, Any]:
        rgb_image = image.convert("RGB")
        try:
            gate, scores = self._identify_with_clip(rgb_image)
            model_used = self.settings.model_id
            note = "Open-source CLIP zero-shot image matching."
        except ModelUnavailableError as exc:
            features = _image_features(rgb_image)
            gate = _local_flora_gate(features)
            scores = self._identify_with_local_fallback(rgb_image, features)
            model_used = "local-color-texture-fallback"
            note = (
                "CLIP dependencies are not installed or the model could not load, "
                f"so a local fallback was used: {exc}"
            )
        if not gate.is_flora:
            return self._build_rejection_result(gate, model_used=model_used, model_note=note)
        return self._build_result(scores, gate=gate, model_used=model_used, model_note=note)

    def _identify_with_clip(self, image: Image.Image) -> tuple[FloraGateResult, list[SpeciesScore]]:
        self._load_clip()
        gate = self._clip_flora_gate(image)
        prompts = [item.prompt() for item in self.species]
        inputs = self._clip_processor(text=prompts, images=image, return_tensors="pt", padding=True)
        with self._torch.no_grad():
            outputs = self._clip_model(**inputs)
            probabilities = outputs.logits_per_image.softmax(dim=1).cpu().numpy()[0]
        return gate, self._scores_from_probabilities(probabilities)

    def _clip_flora_gate(self, image: Image.Image) -> FloraGateResult:
        prompts = [*FLORA_GATE_PROMPTS, *NON_FLORA_GATE_PROMPTS]
        inputs = self._clip_processor(text=prompts, images=image, return_tensors="pt", padding=True)
        with self._torch.no_grad():
            outputs = self._clip_model(**inputs)
            probabilities = outputs.logits_per_image.softmax(dim=1).cpu().numpy()[0]
        flora_probability = float(probabilities[: len(FLORA_GATE_PROMPTS)].sum())
        top_prompt = prompts[int(np.argmax(probabilities))]
        return FloraGateResult(
            is_flora=flora_probability >= self.settings.flora_gate_threshold,
            flora_probability=round(flora_probability, 4),
            top_prompt=top_prompt,
            method="clip-flora-gate",
        )

    def _load_clip(self) -> None:
        if self._clip_model is not None and self._clip_processor is not None:
            return
        try:
            import torch
            from transformers import CLIPModel, CLIPProcessor
        except Exception as exc:  # pragma: no cover - depends on optional packages
            raise ModelUnavailableError(str(exc)) from exc
        try:
            self._clip_model = CLIPModel.from_pretrained(self.settings.model_id)
            self._clip_processor = CLIPProcessor.from_pretrained(self.settings.model_id)
            self._torch = torch
        except Exception as exc:  # pragma: no cover - depends on model download
            raise ModelUnavailableError(str(exc)) from exc

    def _identify_with_local_fallback(
        self,
        image: Image.Image,
        features: dict[str, float] | None = None,
    ) -> list[SpeciesScore]:
        features = features or _image_features(image)
        raw_scores = []
        for item in self.species:
            raw_scores.append(_fallback_species_score(item, features))
        probabilities = _softmax(np.array(raw_scores, dtype=np.float64))
        return self._scores_from_probabilities(probabilities)

    def _scores_from_probabilities(self, probabilities: np.ndarray) -> list[SpeciesScore]:
        pairs = [
            SpeciesScore(species=item, score=float(probabilities[index]))
            for index, item in enumerate(self.species)
        ]
        return sorted(pairs, key=lambda pair: pair.score, reverse=True)

    def _build_result(
        self,
        scores: list[SpeciesScore],
        gate: FloraGateResult,
        model_used: str,
        model_note: str,
    ) -> dict[str, Any]:
        if not scores:
            raise ValueError("No species scores were produced.")

        best = scores[0]
        species = best.species
        confidence = round(best.score, 4)
        status = confidence_status(confidence, self.settings.confidence_threshold)
        similar = _similar_species(species, scores)

        return {
            "status": status,
            "low_confidence_message": low_confidence_message(
                confidence,
                self.settings.confidence_threshold,
            ),
            "common_name": species.common_name,
            "scientific_name": species.scientific_name,
            "category": species.category,
            "confidence": confidence,
            "confidence_percent": f"{confidence * 100:.1f}%",
            "summary": species.summary,
            "fun_facts": species.fun_facts,
            "toxicity_note": species.toxicity_note,
            "origin": species.origin,
            "habitat": species.habitat,
            "regions": species.regions,
            "similar_species": similar,
            "flora_probability": gate.flora_probability,
            "validation_method": gate.method,
            "validation_prompt": gate.top_prompt,
            "model_used": model_used,
            "model_note": model_note,
            "safety_disclaimer": REQUIRED_DISCLAIMER,
            "consumption_warning": CONSUMPTION_WARNING,
        }

    def _build_rejection_result(
        self,
        gate: FloraGateResult,
        model_used: str,
        model_note: str,
    ) -> dict[str, Any]:
        confidence = round(gate.flora_probability, 4)
        return {
            "status": "rejected_non_flora",
            "low_confidence_message": None,
            "common_name": "Unsupported image",
            "scientific_name": "Not applicable",
            "category": "non-flora image",
            "confidence": confidence,
            "confidence_percent": f"{confidence * 100:.1f}%",
            "summary": NON_FLORA_REJECTION_MESSAGE,
            "fun_facts": [
                "Try a clear, well-lit photo of a leaf, flower, tree, mushroom, moss, cactus, fruit, or seed.",
                "Close-up images with the plant or fungus filling most of the frame work best.",
            ],
            "toxicity_note": "No toxicity assessment was made because the upload was rejected.",
            "origin": "No plant or fungus source identified.",
            "habitat": "Not applicable.",
            "regions": [],
            "similar_species": [],
            "flora_probability": confidence,
            "validation_method": gate.method,
            "validation_prompt": gate.top_prompt,
            "rejection_message": NON_FLORA_REJECTION_MESSAGE,
            "model_used": model_used,
            "model_note": model_note,
            "safety_disclaimer": REQUIRED_DISCLAIMER,
            "consumption_warning": CONSUMPTION_WARNING,
        }


def _similar_species(best: FloraSpecies, scores: list[SpeciesScore]) -> list[str]:
    ranked_names = [
        score.species.common_name
        for score in scores[1:6]
        if score.species.common_name not in best.similar_species
    ]
    combined = [*best.similar_species, *ranked_names]
    deduped: list[str] = []
    for name in combined:
        if name not in deduped:
            deduped.append(name)
    return deduped[:5]


def _image_features(image: Image.Image) -> dict[str, float]:
    small = image.resize((96, 96))
    pixels = np.asarray(small).astype(np.float64) / 255.0
    red = pixels[:, :, 0]
    green = pixels[:, :, 1]
    blue = pixels[:, :, 2]
    brightness = float(pixels.mean())
    green_ratio = float(np.mean((green > red * 1.08) & (green > blue * 1.08)))
    warm_ratio = float(np.mean((red > green * 1.08) | ((red + green) / 2 > blue * 1.25)))
    dark_ratio = float(np.mean(pixels.mean(axis=2) < 0.28))
    saturation = float((pixels.max(axis=2) - pixels.min(axis=2)).mean())
    edges = image.convert("L").resize((96, 96)).filter(ImageFilter.FIND_EDGES)
    edge_intensity = float(ImageStat.Stat(edges).mean[0] / 255.0)
    return {
        "brightness": brightness,
        "green_ratio": green_ratio,
        "warm_ratio": warm_ratio,
        "dark_ratio": dark_ratio,
        "saturation": saturation,
        "edge_intensity": edge_intensity,
    }


def _fallback_species_score(species: FloraSpecies, features: dict[str, float]) -> float:
    category = species.category
    score = 1.0
    if category in {"leaf", "plant", "tree", "grass", "moss", "vine", "shrub"}:
        score += features["green_ratio"] * 2.2
    if category in {"flower", "fruit"}:
        score += features["warm_ratio"] * 1.8 + features["saturation"] * 1.2
    if category in {"mushroom", "fungus", "seed"}:
        score += (1.0 - features["green_ratio"]) * 1.1 + features["dark_ratio"] * 0.8
    if category in {"cactus", "succulent"}:
        score += features["green_ratio"] * 1.4 + features["edge_intensity"] * 0.7
    if category == "aquatic plant":
        score += features["green_ratio"] * 1.1 + (1.0 - features["brightness"]) * 0.4
    return score


def _local_flora_gate(features: dict[str, float]) -> FloraGateResult:
    flora_probability = min(
        0.98,
        (
            features["green_ratio"] * 1.75
            + features["warm_ratio"] * 0.45
            + features["saturation"] * 0.85
            + features["edge_intensity"] * 0.55
        ),
    )
    top_prompt = "local color and texture flora signal"
    return FloraGateResult(
        is_flora=flora_probability >= 0.14,
        flora_probability=round(float(flora_probability), 4),
        top_prompt=top_prompt,
        method="local-flora-gate",
    )


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / exp_values.sum()
