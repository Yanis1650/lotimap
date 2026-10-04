from __future__ import annotations

import pytest
from conftest import SAMPLES

from lotimap_importer.config import LayerMapping
from lotimap_importer.convert import convert_dxf


def test_clean_sample_has_twenty_numbered_lots(layers: LayerMapping) -> None:
    result = convert_dxf(SAMPLES / "clos_du_verger_clean.dxf", layers, "EPSG:3949")

    assert result.issues == []
    assert result.lot_count == 20
    assert len(result.features) == 22
    lots = [
        feature for feature in result.features if feature["properties"]["kind"] == "lot"
    ]
    assert sorted(feature["properties"]["number"] for feature in lots) == [
        f"{number:02d}" for number in range(1, 21)
    ]
    assert {feature["properties"]["area_m2"] for feature in lots} == {
        672.0,
        714.0,
        756.0,
        798.0,
        840.0,
        882.0,
        924.0,
        966.0,
        1008.0,
        1050.0,
    }
    longitude, latitude = lots[0]["geometry"]["coordinates"][0][0]
    assert abs(longitude + 1.357) < 0.01
    assert abs(latitude - 48.684) < 0.01


@pytest.mark.parametrize(
    ("variant", "expected_code", "lot_count"),
    [
        ("open_polyline", "open_polyline", 19),
        ("missing_number", "lot_without_number", 20),
        ("duplicate_number", "duplicate_number", 20),
        ("orphan_text", "text_outside_lot", 20),
        ("invalid_geometry", "invalid_geometry", 19),
    ],
)
def test_broken_samples_continue_conversion(
    layers: LayerMapping, variant: str, expected_code: str, lot_count: int
) -> None:
    result = convert_dxf(SAMPLES / f"clos_du_verger_{variant}.dxf", layers, "EPSG:3949")

    assert not result.fatal
    assert result.lot_count == lot_count
    assert expected_code in {issue.code for issue in result.issues}
    assert result.geojson()["type"] == "FeatureCollection"


def test_mapping_is_case_insensitive(layers: LayerMapping) -> None:
    lowercase = LayerMapping(
        lots=frozenset({"lots"}),
        numbers=frozenset({"numeros_lots"}),
        roads=frozenset({"voirie"}),
        boundary=frozenset({"limite_operation"}),
    )
    result = convert_dxf(SAMPLES / "clos_du_verger_clean.dxf", lowercase, "EPSG:3949")
    assert result.lot_count == 20
