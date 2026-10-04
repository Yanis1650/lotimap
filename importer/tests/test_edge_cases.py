from __future__ import annotations

from pathlib import Path

import ezdxf
import pytest
from pyproj import Transformer

from lotimap_importer.config import ConfigError, LayerMapping, load_mapping
from lotimap_importer.convert import convert_dxf


def make_dxf(path: Path, *, kind: str = "POLYLINE") -> None:
    center_x, center_y = Transformer.from_crs(
        "EPSG:4326", "EPSG:2154", always_xy=True
    ).transform(-1.357, 48.684)
    corners = [
        (center_x, center_y),
        (center_x + 20, center_y),
        (center_x + 20, center_y + 30),
        (center_x, center_y + 30),
    ]
    document = ezdxf.new("R2010")
    space = document.modelspace()
    if kind == "POLYLINE":
        space.add_polyline2d(corners, close=True, dxfattribs={"layer": "PARCELLES"})
    elif kind == "CURVE":
        space.add_lwpolyline(
            [(x, y, 1 if index == 0 else 0) for index, (x, y) in enumerate(corners)],
            format="xyb",
            close=True,
            dxfattribs={"layer": "PARCELLES"},
        )
    else:
        space.add_line(corners[0], corners[1], dxfattribs={"layer": "PARCELLES"})
    space.add_text(
        "A1",
        dxfattribs={"insert": (center_x + 10, center_y + 15), "layer": "ETIQUETTES"},
    )
    document.saveas(path)


@pytest.fixture
def custom_layers() -> LayerMapping:
    return LayerMapping(
        lots=frozenset({"parcelles"}),
        numbers=frozenset({"etiquettes"}),
        roads=frozenset(),
        boundary=frozenset(),
    )


def test_lambert93_polyline_and_custom_layers(
    tmp_path: Path, custom_layers: LayerMapping
) -> None:
    path = tmp_path / "lambert93.dxf"
    make_dxf(path)

    result = convert_dxf(path, custom_layers, "EPSG:2154")

    assert result.issues == []
    assert result.lot_count == 1
    assert result.features[0]["properties"]["area_m2"] == 600.0
    assert result.features[0]["properties"]["number"] == "A1"


@pytest.mark.parametrize(
    ("kind", "expected"),
    [("CURVE", "curved_segment"), ("LINE", "unsupported_entity")],
)
def test_unsupported_geometry_is_reported(
    tmp_path: Path, custom_layers: LayerMapping, kind: str, expected: str
) -> None:
    path = tmp_path / "unsupported.dxf"
    make_dxf(path, kind=kind)

    result = convert_dxf(path, custom_layers, "EPSG:2154")

    assert result.lot_count == 0
    assert expected in {issue.code for issue in result.issues}


def test_unreadable_file_returns_fatal_report(
    tmp_path: Path, custom_layers: LayerMapping
) -> None:
    path = tmp_path / "broken.dxf"
    path.write_text("not a DXF file", encoding="utf-8")

    result = convert_dxf(path, custom_layers, "EPSG:2154")

    assert result.fatal
    assert result.issues[0].code == "dxf_read_error"


@pytest.mark.parametrize(
    "yaml_text",
    ["lots: [LOTS]\nnumbers: [LOTS]\n", "lots: LOTS\nnumbers: [NUMBERS]\n"],
)
def test_invalid_layer_mapping_is_rejected(tmp_path: Path, yaml_text: str) -> None:
    path = tmp_path / "layers.yaml"
    path.write_text(yaml_text, encoding="utf-8")
    with pytest.raises(ConfigError):
        load_mapping(path)
