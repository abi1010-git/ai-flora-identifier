from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class FloraSpecies:
    id: str
    common_name: str
    scientific_name: str
    category: str
    summary: str
    fun_facts: list[str]
    toxicity_note: str
    origin: str
    habitat: str
    regions: list[str]
    similar_species: list[str]
    prompt_terms: list[str]

    @classmethod
    def from_dict(cls, data: dict) -> "FloraSpecies":
        return cls(
            id=str(data["id"]),
            common_name=str(data["common_name"]),
            scientific_name=str(data["scientific_name"]),
            category=str(data["category"]),
            summary=str(data["summary"]),
            fun_facts=list(data.get("fun_facts", [])),
            toxicity_note=str(data["toxicity_note"]),
            origin=str(data["origin"]),
            habitat=str(data["habitat"]),
            regions=list(data.get("regions", [])),
            similar_species=list(data.get("similar_species", [])),
            prompt_terms=list(data.get("prompt_terms", [])),
        )

    def prompt(self) -> str:
        terms = ", ".join(self.prompt_terms)
        return (
            f"a clear nature photo of {self.common_name}, scientific name "
            f"{self.scientific_name}, category {self.category}, {terms}"
        )


def load_catalog(path: Path) -> list[FloraSpecies]:
    with path.open("r", encoding="utf-8") as file:
        raw_species = json.load(file)
    species = [FloraSpecies.from_dict(item) for item in raw_species]
    if not species:
        raise ValueError("The flora catalog is empty.")
    _validate_unique_ids(species)
    return species


def catalog_categories(species: Iterable[FloraSpecies]) -> set[str]:
    return {item.category for item in species}


def _validate_unique_ids(species: Iterable[FloraSpecies]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in species:
        if item.id in seen:
            duplicates.add(item.id)
        seen.add(item.id)
    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        raise ValueError(f"Duplicate flora catalog ids: {duplicate_list}")

