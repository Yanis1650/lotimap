from __future__ import annotations

from decimal import Decimal

from enrichment.dvf import commune_median, prices_per_m2
from enrichment.plu import assign_zones
from enrichment.risks import commune_risks


def row(mutation: str, parcel: str, area: str, value: str = "150000") -> dict[str, str]:
    return {
        "code_commune": "50025",
        "nature_mutation": "Vente terrain à bâtir",
        "id_mutation": mutation,
        "numero_disposition": "000001",
        "id_parcelle": parcel,
        "surface_terrain": area,
        "valeur_fonciere": value,
        "type_local": "",
        "code_type_local": "",
        "code_nature_culture": "AB",
        "code_nature_culture_speciale": "",
    }


def test_dvf_counts_one_price_per_mutation_and_deduplicates_surface() -> None:
    rows = [row("a", "p1", "1000"), row("a", "p1", "1000"), row("a", "p2", "500")]
    rows[-1]["numero_disposition"] = "000002"
    built = row("b", "p3", "500")
    built["type_local"] = "Maison"
    regular = row("c", "p4", "500")
    regular["nature_mutation"] = "Vente"
    assert prices_per_m2(rows + [built, regular], "50025") == [Decimal(100)]


def test_dvf_suppresses_small_sample(monkeypatch) -> None:
    monkeypatch.setattr(
        "enrichment.dvf.fetch_csv", lambda _url: [row("a", "p1", "1000")]
    )
    result = commune_median("50025", [2025])
    assert result == {"median_eur_m2": None, "sample_size": 1, "years": [2025]}


def test_plu_reports_mixed_zone_and_partial_coverage() -> None:
    lot = {
        "id": "lot-1",
        "properties": {"kind": "lot"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [[-1, 48], [-0.99, 48], [-0.99, 48.01], [-1, 48.01], [-1, 48]]
            ],
        },
    }
    zones = [
        {
            "properties": {
                "libelle": code,
                "libelong": code,
                "gpu_status": "production",
            },
            "geometry": {"type": "Polygon", "coordinates": [ring]},
        }
        for code, ring in (
            ("U", [[-1, 48], [-0.995, 48], [-0.995, 48.01], [-1, 48.01], [-1, 48]]),
            (
                "N",
                [
                    [-0.995, 48],
                    [-0.99, 48],
                    [-0.99, 48.01],
                    [-0.995, 48.01],
                    [-0.995, 48],
                ],
            ),
        )
    ]
    result = assign_zones([lot], zones, "EPSG:3949")["lot-1"]
    assert set(result["code"].split(" / ")) == {"U", "N"}
    assert result["coverage_pct"] == 100
    assert assign_zones([lot], zones[:1], "EPSG:3949")["lot-1"]["code"] is None
    overlapping = [zones[0], {**zones[1], "geometry": zones[0]["geometry"]}]
    assert assign_zones([lot], overlapping, "EPSG:3949")["lot-1"]["code"] is None


def test_georisques_keeps_only_communal_families(monkeypatch) -> None:
    monkeypatch.setattr(
        "enrichment.risks.fetch_json",
        lambda *_args: {
            "data": [
                {
                    "code_insee": "50025",
                    "risques_detail": [
                        {"num_risque": "11", "libelle_risque_long": "Inondation"},
                        {"num_risque": "112", "libelle_risque_long": "Crue"},
                    ],
                }
            ],
        },
    )
    assert commune_risks("50025") == ["Inondation"]
