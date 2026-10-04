"""Produit uniquement des indicateurs publics agrégés pour un plan donné."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from .dvf import SOURCE_ROOT as DVF_URL
from .dvf import commune_median
from .plu import SOURCE_URL as GPU_URL
from .plu import assign_zones, fetch_zones
from .risks import SOURCE_URL as RISKS_URL
from .risks import commune_risks

ROOT = Path(__file__).resolve().parents[1]


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan", type=Path, default=ROOT / "data/demo/geojson/clos_du_verger.geojson"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "data/demo/enrichment.json"
    )
    parser.add_argument("--commune-code", default="50025")
    parser.add_argument("--commune-name", default="Avranches")
    parser.add_argument(
        "--area-crs", choices=("EPSG:2154", "EPSG:3949"), default="EPSG:3949"
    )
    parser.add_argument("--start-year", type=int, default=2021)
    parser.add_argument("--end-year", type=int, default=2025)
    return parser.parse_args()


def main() -> None:
    args = arguments()
    if not args.commune_code.isdigit() or len(args.commune_code) != 5:
        raise SystemExit("Le code INSEE doit contenir cinq chiffres.")
    if args.start_year > args.end_year or args.end_year - args.start_year > 4:
        raise SystemExit("Choisir une période de un à cinq ans.")
    years = list(range(args.start_year, args.end_year + 1))
    plan_bytes = args.plan.read_bytes()
    features = json.loads(plan_bytes)["features"]
    if not any(item["properties"]["kind"] == "lot" for item in features):
        raise SystemExit("Le plan ne contient aucun lot.")

    zones = fetch_zones(features)
    plu = assign_zones(features, zones, args.area_crs)
    risks = commune_risks(args.commune_code)
    dvf = commune_median(args.commune_code, years)
    date = datetime.now(UTC).date().isoformat()
    document_dates = sorted(
        {
            feature.get("properties", {}).get("datvalid")
            for feature in zones
            if feature.get("properties", {}).get("datvalid")
        }
    )
    result = {
        "schema_version": 1,
        "generated_on": date,
        "plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
        "commune": {"code": args.commune_code, "name": args.commune_name},
        "plu": plu,
        "risks": {"scope": "commune", "families": risks},
        "dvf": dvf,
        "sources": {
            "gpu": {
                "url": GPU_URL,
                "consulted_on": date,
                "document_dates": document_dates,
            },
            "georisques": {"url": RISKS_URL, "consulted_on": date},
            "dvf": {"url": DVF_URL, "consulted_on": date},
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    matched = sum(item["code"] is not None for item in plu.values())
    print(
        f"PLU : {matched}/{len(plu)} lots attribués · Géorisques : {len(risks)} familles communales"
    )
    print(
        f"DVF {years[0]}–{years[-1]} : {dvf['sample_size']} mutations · médiane {dvf['median_eur_m2']} €/m²"
    )
    print(f"Enrichissement écrit : {args.output}")


if __name__ == "__main__":
    main()
