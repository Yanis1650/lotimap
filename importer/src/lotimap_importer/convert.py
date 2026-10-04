"""Recover a DXF document and convert configured layers to WGS84 features."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from ezdxf import recover
from ezdxf.audit import ErrorEntry
from pyproj import Transformer
from shapely.geometry import Polygon

from .association import attach_numbers
from .config import LayerMapping
from .geometry import (
    GeometryError,
    number_from_entity,
    polygon_from_entity,
    wgs84_geometry,
)
from .models import ConversionResult, Issue, Lot, NumberText

SOURCE_CRS = {"EPSG:2154", "EPSG:3949"}
FEATURE_KINDS = {"roads": "road", "boundary": "operation_boundary"}


def audit_issue(
    entry: ErrorEntry, code: str, severity: Literal["warning", "error"]
) -> Issue:
    entity = entry.entity
    layer = entity.dxf.get("layer") if entity is not None else None
    handle = entity.dxf.get("handle") if entity is not None else None
    return Issue(
        code,
        f"DXF {entry.code} : {entry.message}",
        severity=severity,
        layer=layer,
        handle=handle,
    )


def make_feature(
    polygon: Polygon,
    kind: str,
    layer: str,
    handle: str,
    transformer: Transformer,
    number: str | None = None,
) -> dict[str, Any]:
    properties: dict[str, Any] = {"kind": kind, "layer": layer}
    if kind == "lot":
        properties.update(number=number, area_m2=round(polygon.area, 2))
    return {
        "type": "Feature",
        "id": f"{kind}-{handle}",
        "geometry": wgs84_geometry(polygon, transformer),
        "properties": properties,
    }


def convert_dxf(
    input_path: Path, layers: LayerMapping, source_crs: str
) -> ConversionResult:
    if source_crs not in SOURCE_CRS:
        raise ValueError("La projection source doit être EPSG:2154 ou EPSG:3949.")
    result = ConversionResult(source_crs=source_crs)
    try:
        document, auditor = recover.readfile(input_path)
    except Exception as error:  # noqa: BLE001 - a damaged DXF must yield a report
        result.fatal = True
        result.issues.append(
            Issue(
                "dxf_read_error", f"Lecture DXF impossible : {error}", severity="error"
            )
        )
        return result

    for error in auditor.errors:
        result.issues.append(audit_issue(error, "dxf_audit_error", "error"))
    for fix in auditor.fixes:
        result.issues.append(audit_issue(fix, "dxf_repair", "warning"))

    transformer = Transformer.from_crs(source_crs, "EPSG:4326", always_xy=True)
    lots: list[Lot] = []
    numbers: list[NumberText] = []
    for entity in document.modelspace():
        layer = entity.dxf.get("layer", "0")
        category = layers.category(layer)
        if category is None:
            continue
        handle = entity.dxf.get("handle", "?")
        try:
            if category == "numbers":
                value, point = number_from_entity(entity)
                numbers.append(NumberText(value, point, layer, handle))
                continue
            polygon = polygon_from_entity(entity)
            if category == "lots":
                lots.append(Lot(polygon, layer, handle))
            else:
                result.features.append(
                    make_feature(
                        polygon, FEATURE_KINDS[category], layer, handle, transformer
                    )
                )
        except GeometryError as error:
            result.issues.append(
                Issue(error.code, str(error), layer=layer, handle=handle)
            )
        except Exception as error:  # noqa: BLE001 - keep processing other entities
            result.issues.append(
                Issue(
                    "entity_error",
                    f"Entité ignorée après erreur : {error}",
                    layer=layer,
                    handle=handle,
                )
            )

    if not lots:
        result.issues.append(Issue("no_valid_lots", "Aucun lot valide trouvé."))
    attach_numbers(lots, numbers, result.issues)
    for lot in lots:
        number = lot.numbers[0].value if len(lot.numbers) == 1 else None
        result.features.append(
            make_feature(lot.polygon, "lot", lot.layer, lot.handle, transformer, number)
        )
    return result
