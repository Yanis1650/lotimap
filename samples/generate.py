# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["ezdxf>=1.4,<2", "pyproj>=3.7,<4"]
# ///
"""Generate the fictional Clos du Verger DXF plan and broken fixtures."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from plan import LAYERS, LOTS_PER_SIDE, SOURCE_CRS, VARIANTS, Layout, build_document
from pyproj import Transformer


def generate(layout: Layout, output_dir: Path) -> list[Path]:
    layout.validate()
    output_dir.mkdir(parents=True, exist_ok=True)
    transformer = Transformer.from_crs("EPSG:4326", SOURCE_CRS, always_xy=True)
    center_x, center_y = transformer.transform(layout.center_lon, layout.center_lat)

    output_paths = []
    fixtures = []
    for variant, expected_issue in VARIANTS:
        filename = f"clos_du_verger_{variant}.dxf"
        path = output_dir / filename
        build_document(layout, variant, center_x, center_y).saveas(path)
        output_paths.append(path)
        fixtures.append(
            {
                "file": filename,
                "variant": variant,
                "expected_issue": expected_issue,
            }
        )

    manifest = {
        "scenario": "Le Clos du Verger (fictif)",
        "source_crs": SOURCE_CRS,
        "center_wgs84": {"latitude": layout.center_lat, "longitude": layout.center_lon},
        "center_cc49": {"easting": round(center_x, 3), "northing": round(center_y, 3)},
        "layout": asdict(layout),
        "lot_count": 2 * LOTS_PER_SIDE,
        "layers": LAYERS,
        "fixtures": fixtures,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return [*output_paths, manifest_path]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center-lat", type=float, default=Layout.center_lat)
    parser.add_argument("--center-lon", type=float, default=Layout.center_lon)
    parser.add_argument("--rotation-deg", type=float, default=Layout.rotation_deg)
    parser.add_argument("--frontage-m", type=float, default=Layout.frontage_m)
    parser.add_argument("--depth-m", type=float, default=Layout.depth_m)
    parser.add_argument("--road-width-m", type=float, default=Layout.road_width_m)
    parser.add_argument("--margin-m", type=float, default=Layout.margin_m)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "demo" / "dxf",
    )
    args = parser.parse_args()
    layout = Layout(
        center_lat=args.center_lat,
        center_lon=args.center_lon,
        rotation_deg=args.rotation_deg,
        frontage_m=args.frontage_m,
        depth_m=args.depth_m,
        road_width_m=args.road_width_m,
        margin_m=args.margin_m,
    )
    try:
        paths = generate(layout, args.output_dir)
    except ValueError as error:
        parser.error(str(error))
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
