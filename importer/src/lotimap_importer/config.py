"""Load the user supplied DXF layer mapping."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

Category = Literal["lots", "numbers", "roads", "boundary"]
CATEGORIES: tuple[Category, ...] = ("lots", "numbers", "roads", "boundary")


class ConfigError(ValueError):
    """The layer mapping is missing or ambiguous."""


@dataclass(frozen=True)
class LayerMapping:
    lots: frozenset[str]
    numbers: frozenset[str]
    roads: frozenset[str]
    boundary: frozenset[str]

    def category(self, layer: str) -> Category | None:
        name = layer.casefold()
        for category in CATEGORIES:
            if name in getattr(self, category):
                return category
        return None


def load_mapping(path: Path) -> LayerMapping:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise ConfigError(f"Impossible de lire le mapping {path}: {error}") from error
    if not isinstance(raw, dict):
        raise ConfigError(
            "Le mapping doit être un objet YAML avec des listes de calques."
        )

    unknown = set(raw) - set(CATEGORIES)
    if unknown:
        raise ConfigError(f"Clés de mapping inconnues : {', '.join(map(str, unknown))}")

    normalized: dict[Category, frozenset[str]] = {}
    seen: set[str] = set()
    for category in CATEGORIES:
        values = raw.get(category, [])
        if not isinstance(values, list) or not all(
            isinstance(value, str) and value.strip() for value in values
        ):
            raise ConfigError(f"{category} doit être une liste de noms non vides.")
        names = frozenset(value.strip().casefold() for value in values)
        overlap = seen & names
        if overlap:
            raise ConfigError(
                f"Calque présent dans plusieurs catégories : {overlap.pop()}"
            )
        seen.update(names)
        normalized[category] = names

    if not normalized["lots"] or not normalized["numbers"]:
        raise ConfigError("Les catégories lots et numbers doivent être renseignées.")
    return LayerMapping(**normalized)
