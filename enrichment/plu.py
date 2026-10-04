"""Croisement des lots avec les zones d'urbanisme de l'API Carto GPU."""

from __future__ import annotations

import json
from collections import defaultdict

from pyproj import Transformer
from shapely.geometry import mapping, shape
from shapely.ops import transform, unary_union

from .fetch import fetch_json
from .models import JsonObject, PluMatch

SOURCE_URL = "https://apicarto.ign.fr/api/gpu/zone-urba"


def fetch_zones(features: list[JsonObject]) -> list[JsonObject]:
    boundary = next(
        (
            item["geometry"]
            for item in features
            if item["properties"]["kind"] == "operation_boundary"
        ),
        None,
    )
    if boundary is None:
        polygons = [
            shape(item["geometry"])
            for item in features
            if item["properties"]["kind"] == "lot"
        ]
        boundary = mapping(unary_union(polygons))
    response = fetch_json(
        SOURCE_URL, {"geom": json.dumps(boundary, separators=(",", ":"))}
    )
    zones = response.get("features")
    if not isinstance(zones, list):
        raise TypeError("Réponse GPU sans liste de zones.")
    return zones


def assign_zones(
    features: list[JsonObject], zones: list[JsonObject], area_crs: str
) -> dict[str, PluMatch]:
    project = Transformer.from_crs("EPSG:4326", area_crs, always_xy=True).transform
    grouped: dict[str, list] = defaultdict(list)
    descriptions: dict[str, str | None] = {}
    for feature in zones:
        props = feature.get("properties") or {}
        code = props.get("libelle")
        if not code or props.get("gpu_status") not in (None, "production"):
            continue
        grouped[code].append(transform(project, shape(feature["geometry"])))
        descriptions[code] = props.get("libelong")
    projected = {code: unary_union(polygons) for code, polygons in grouped.items()}
    covered_geometry = unary_union(list(projected.values()))

    result: dict[str, PluMatch] = {}
    for feature in features:
        if feature["properties"]["kind"] != "lot":
            continue
        lot = transform(project, shape(feature["geometry"]))
        if not lot.is_valid or lot.area <= 0:
            raise ValueError(f"Lot invalide pour le croisement PLU : {feature['id']}")
        areas = {
            code: lot.intersection(geometry).area
            for code, geometry in projected.items()
        }
        ordered = sorted(areas, key=lambda code: areas[code], reverse=True)
        codes = [code for code in ordered if areas[code] / lot.area >= 0.01]
        coverage = min(1.0, lot.intersection(covered_geometry).area / lot.area)
        valid = coverage >= 0.95 and bool(codes)
        result[feature["id"]] = {
            "code": " / ".join(codes) if valid else None,
            "description": descriptions.get(codes[0])
            if valid and len(codes) == 1
            else None,
            "coverage_pct": round(coverage * 100),
        }
    return result
