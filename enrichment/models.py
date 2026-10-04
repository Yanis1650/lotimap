from __future__ import annotations

from typing import Any, TypedDict

JsonObject = dict[str, Any]


class PluMatch(TypedDict):
    code: str | None
    description: str | None
    coverage_pct: int


class DvfIndicator(TypedDict):
    median_eur_m2: int | None
    sample_size: int
    years: list[int]
