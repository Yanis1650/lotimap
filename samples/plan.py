"""Geometry and DXF construction for the fictional lotissement."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Literal

import ezdxf
from ezdxf.document import Drawing
from ezdxf.enums import TextEntityAlignment

ezdxf.options.write_fixed_meta_data_for_testing = True

SOURCE_CRS = "EPSG:3949"
LOTS_PER_SIDE = 10
MIN_DEPTH_FACTOR = 0.8
DEPTH_STEP = 0.05
MAX_DEPTH_FACTOR = MIN_DEPTH_FACTOR + DEPTH_STEP * (LOTS_PER_SIDE - 1)
LAYERS = {
    "lots": "LOTS",
    "road": "VOIRIE",
    "boundary": "LIMITE_OPERATION",
    "numbers": "NUMEROS_LOTS",
}
Variant = Literal[
    "clean",
    "open_polyline",
    "missing_number",
    "duplicate_number",
    "orphan_text",
    "invalid_geometry",
]
VARIANTS: tuple[tuple[Variant, str | None], ...] = (
    ("clean", None),
    ("open_polyline", "lot 01: polyligne non fermée"),
    ("missing_number", "lot 02: numéro absent"),
    ("duplicate_number", "lot 04: numéro 03 répété"),
    ("orphan_text", "texte 99 hors de tous les lots"),
    ("invalid_geometry", "lot 05: polygone auto-intersecté"),
)


@dataclass(frozen=True)
class Layout:
    center_lat: float = 48.684
    center_lon: float = -1.357
    rotation_deg: float = 0.0
    frontage_m: float = 24.0
    depth_m: float = 35.0
    road_width_m: float = 10.0
    margin_m: float = 5.0

    def validate(self) -> None:
        values = asdict(self)
        if not all(math.isfinite(value) for value in values.values()):
            raise ValueError("Tous les paramètres numériques doivent être finis.")
        if not -90 <= self.center_lat <= 90 or not -180 <= self.center_lon <= 180:
            raise ValueError("La latitude ou la longitude est hors plage.")
        for name in ("frontage_m", "depth_m", "road_width_m"):
            if values[name] <= 0:
                raise ValueError(f"{name} doit être strictement positif.")
        if self.margin_m < 0:
            raise ValueError("margin_m ne peut pas être négatif.")


def local_to_cc49(
    x: float,
    y: float,
    center_x: float,
    center_y: float,
    rotation_rad: float,
) -> tuple[float, float]:
    cosine = math.cos(rotation_rad)
    sine = math.sin(rotation_rad)
    return (
        center_x + x * cosine - y * sine,
        center_y + x * sine + y * cosine,
    )


def rectangle(
    left: float, bottom: float, right: float, top: float
) -> list[tuple[float, float]]:
    return [(left, bottom), (right, bottom), (right, top), (left, top)]


def build_document(
    layout: Layout, variant: Variant, center_x: float, center_y: float
) -> Drawing:
    document = ezdxf.new("R2010")
    document.header["$INSUNITS"] = 6  # metres
    document.header["$MEASUREMENT"] = 1
    for layer, color in (
        (LAYERS["lots"], 3),
        (LAYERS["road"], 8),
        (LAYERS["boundary"], 1),
        (LAYERS["numbers"], 7),
    ):
        document.layers.new(layer, dxfattribs={"color": color})

    modelspace = document.modelspace()
    rotation_rad = math.radians(layout.rotation_deg)

    def projected(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [
            local_to_cc49(x, y, center_x, center_y, rotation_rad) for x, y in points
        ]

    half_road = layout.road_width_m / 2
    half_lots = LOTS_PER_SIDE * layout.frontage_m / 2
    outer_x = half_lots + layout.margin_m
    outer_y = half_road + layout.depth_m * MAX_DEPTH_FACTOR + layout.margin_m

    modelspace.add_lwpolyline(
        projected(rectangle(-outer_x, -outer_y, outer_x, outer_y)),
        close=True,
        dxfattribs={"layer": LAYERS["boundary"]},
    )
    modelspace.add_lwpolyline(
        projected(rectangle(-outer_x, -half_road, outer_x, half_road)),
        close=True,
        dxfattribs={"layer": LAYERS["road"]},
    )

    for side in range(2):
        for column in range(LOTS_PER_SIDE):
            number = side * LOTS_PER_SIDE + column + 1
            left = -half_lots + column * layout.frontage_m
            right = left + layout.frontage_m
            depth_factor = MIN_DEPTH_FACTOR + DEPTH_STEP * (
                (column + 5 * side) % LOTS_PER_SIDE
            )
            lot_depth = layout.depth_m * depth_factor
            bottom, top = (
                (half_road, half_road + lot_depth)
                if side == 0
                else (-half_road - lot_depth, -half_road)
            )
            points = rectangle(left, bottom, right, top)
            if variant == "invalid_geometry" and number == 5:
                points = [points[0], points[2], points[1], points[3]]

            modelspace.add_lwpolyline(
                projected(points),
                close=not (variant == "open_polyline" and number == 1),
                dxfattribs={"layer": LAYERS["lots"]},
            )

            if variant == "missing_number" and number == 2:
                continue
            label = (
                "03"
                if variant == "duplicate_number" and number == 4
                else f"{number:02d}"
            )
            label_x = (
                left + layout.frontage_m / 4
                if variant == "invalid_geometry" and number == 5
                else (left + right) / 2
            )
            text_x, text_y = local_to_cc49(
                label_x,
                (bottom + top) / 2,
                center_x,
                center_y,
                rotation_rad,
            )
            if number % 2:
                modelspace.add_text(
                    label,
                    dxfattribs={"layer": LAYERS["numbers"], "height": 3.0},
                ).set_placement(
                    (text_x, text_y), align=TextEntityAlignment.MIDDLE_CENTER
                )
            else:
                modelspace.add_mtext(
                    label,
                    dxfattribs={"layer": LAYERS["numbers"], "char_height": 3.0},
                ).set_location((text_x, text_y), attachment_point=5)

    if variant == "orphan_text":
        text_x, text_y = local_to_cc49(
            outer_x + 20,
            0,
            center_x,
            center_y,
            rotation_rad,
        )
        modelspace.add_text(
            "99",
            dxfattribs={"layer": LAYERS["numbers"], "height": 3.0},
        ).set_placement((text_x, text_y), align=TextEntityAlignment.MIDDLE_CENTER)

    # Keep class records in a stable order so regenerated fixtures have clean diffs.
    document.classes.add_required_classes(document.dxfversion)
    document.classes.classes = dict(sorted(document.classes.classes.items()))
    return document
