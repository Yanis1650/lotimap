"""Médiane communale des ventes de terrains à bâtir, à la mutation."""

from __future__ import annotations

from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from statistics import median

from .fetch import fetch_csv
from .models import DvfIndicator

SOURCE_ROOT = "https://files.data.gouv.fr/geo-dvf/latest/csv"
MIN_SAMPLE = 5


def _positive(value: str | None) -> Decimal | None:
    try:
        number = Decimal(value or "")
        return number if number.is_finite() and number > 0 else None
    except InvalidOperation:
        return None


def prices_per_m2(rows: list[dict[str, str]], commune: str) -> list[Decimal]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("code_commune") != commune:
            continue
        if row.get("nature_mutation", "").strip() != "Vente terrain à bâtir":
            continue
        mutation_id = row.get("id_mutation", "")
        if mutation_id:
            groups[mutation_id].append(row)

    prices = []
    for mutation in groups.values():
        if any(row.get("type_local") or row.get("code_type_local") for row in mutation):
            continue
        values = {_positive(row.get("valeur_fonciere")) for row in mutation}
        if len(values) != 1 or None in values:
            continue
        surfaces: dict[tuple[str, str, str, Decimal], Decimal] = {}
        for row in mutation:
            area = _positive(row.get("surface_terrain"))
            if area is None or not row.get("id_parcelle"):
                surfaces.clear()
                break
            key = (
                row["id_parcelle"],
                row.get("code_nature_culture", ""),
                row.get("code_nature_culture_speciale", ""),
                area,
            )
            surfaces[key] = area
        total_area = sum(surfaces.values(), Decimal(0))
        if total_area > 0:
            prices.append(next(iter(values)) / total_area)
    return prices


def commune_median(commune: str, years: list[int]) -> DvfIndicator:
    prices: list[Decimal] = []
    for year in years:
        url = f"{SOURCE_ROOT}/{year}/communes/{commune[:2]}/{commune}.csv"
        prices.extend(prices_per_m2(fetch_csv(url), commune))
    value = median(prices) if len(prices) >= MIN_SAMPLE else None
    rounded = int(value.quantize(Decimal(1), rounding=ROUND_HALF_UP)) if value else None
    return {"median_eur_m2": rounded, "sample_size": len(prices), "years": years}
