"""Extract projected polygons and label positions from DXF entities."""

from __future__ import annotations

from typing import Any

from ezdxf.entities import DXFEntity
from pyproj import Transformer
from shapely.geometry import Point, Polygon, mapping
from shapely.ops import transform
from shapely.validation import explain_validity


class GeometryError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def polygon_from_entity(entity: DXFEntity) -> Polygon:
    kind = entity.dxftype()
    if kind == "LWPOLYLINE":
        if not entity.closed:
            raise GeometryError("open_polyline", "Polyligne non fermée.")
        points = list(entity.get_points("xyb"))
        coordinates = [(x, y) for x, y, _ in points]
        bulges = [bulge for _, _, bulge in points]
    elif kind == "POLYLINE":
        if not entity.is_closed:
            raise GeometryError("open_polyline", "Polyligne non fermée.")
        if entity.is_3d_polyline:
            raise GeometryError("unsupported_3d", "Polyligne 3D non prise en charge.")
        coordinates = [
            (vertex.dxf.location.x, vertex.dxf.location.y) for vertex in entity.vertices
        ]
        bulges = [vertex.dxf.get("bulge", 0) for vertex in entity.vertices]
    else:
        raise GeometryError("unsupported_entity", f"Entité {kind} non prise en charge.")

    if any(bulge != 0 for bulge in bulges):
        raise GeometryError("curved_segment", "Segment courbe non pris en charge.")
    if len(set(coordinates)) < 3:
        raise GeometryError("invalid_geometry", "Moins de trois sommets distincts.")
    polygon = Polygon(coordinates)
    if not polygon.is_valid or polygon.area <= 0:
        raise GeometryError("invalid_geometry", explain_validity(polygon))
    return polygon


def number_from_entity(entity: DXFEntity) -> tuple[str, Point]:
    kind = entity.dxftype()
    if kind == "TEXT":
        text = entity.dxf.text.strip()
        aligned = entity.dxf.get("halign", 0) or entity.dxf.get("valign", 0)
        position = entity.dxf.align_point if aligned else entity.dxf.insert
    elif kind == "MTEXT":
        text = entity.plain_text().strip()
        position = entity.dxf.insert
    else:
        raise GeometryError("unsupported_entity", f"Entité {kind} non prise en charge.")
    if not text:
        raise GeometryError("empty_number", "Texte de numéro vide.")
    return text, Point(position.x, position.y)


def wgs84_geometry(polygon: Polygon, transformer: Transformer) -> dict[str, Any]:
    return mapping(transform(transformer.transform, polygon))
