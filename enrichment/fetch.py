"""Lectures ponctuelles des sources officielles, jamais depuis le serveur web."""

from __future__ import annotations

import csv
import io
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import JsonObject

USER_AGENT = "lotimap-open-data-demo/0.1"


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read()


def fetch_json(url: str, params: dict[str, str]) -> JsonObject:
    query = urlencode(params)
    data = json.loads(fetch_bytes(f"{url}?{query}"))
    if not isinstance(data, dict):
        raise TypeError(f"Réponse JSON inattendue : {url}")
    return data


def fetch_csv(url: str) -> list[dict[str, str]]:
    text = fetch_bytes(url).decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))
