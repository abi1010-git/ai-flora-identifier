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
            scores = self._identify_with_clip(rgb_image)
            model_used = self.settings.model_id
            note = "Open-source CLIP zero-shot image matching."
        except ModelUnavailableError as exc:
            scores = self._identify_with_local_fallback(rgb_image)
            model_used = "local-color-texture-fallback"
            note = (
                "CLIP dependencies are not installed or the model could not load, "
                f"so a local fallback was used: {exc}"
            )
        return self._build_result(scores, model_used=model_used, model_note=note)

    def _identify_with_clip(self, image: Image.Image) -> list[SpeciesScore]:
        self._load_clip()
        prompts = [item.prompt() for item in self.species]
        inputs = self._clip_processor(text=prompts, images=image, return_tensors="pt", padding=True)
        with self._torch.no_grad():
            outputs = self._clip_model(**inputs)
            probabilities = outputs.logits_per_image.softmax(dim=1).cpu().numpy()[0]
        return self._scores_from_probabilities(probabilities)

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

    def _identify_with_local_fallback(self, image: Image.Image) -> list[SpeciesScore]:
        features = _image_features(image)
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


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / exp_values.sum()

