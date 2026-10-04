"""Risques GASPAR recensés à l'échelle de la commune."""

from __future__ import annotations

from .fetch import fetch_json

SOURCE_URL = "https://georisques.gouv.fr/api/v1/gaspar/risques"


def commune_risks(code: str) -> list[str]:
    response = fetch_json(SOURCE_URL, {"code_insee": code})
    records = response.get("data")
    if not isinstance(records, list):
        raise TypeError("Réponse Géorisques sans liste de communes.")
    commune = next((item for item in records if item.get("code_insee") == code), None)
    if commune is None:
        raise ValueError(f"Commune {code} absente de la réponse Géorisques.")
    details = commune.get("risques_detail")
    if not isinstance(details, list):
        raise TypeError("Réponse Géorisques sans détail des risques.")
    families = {
        item["libelle_risque_long"]
        for item in details
        if isinstance(item, dict)
        and len(str(item.get("num_risque", ""))) == 2
        and isinstance(item.get("libelle_risque_long"), str)
    }
    return sorted(families)
