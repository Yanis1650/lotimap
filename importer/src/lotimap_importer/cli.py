"""Command line interface for the DXF to GeoJSON converter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from .config import ConfigError, load_mapping
from .convert import convert_dxf
from .report import format_report

app = typer.Typer(help="Convertir un plan DXF en GeoJSON contrôlé.")


@app.command()
def convert(
    input_dxf: Annotated[Path, typer.Argument(help="Plan DXF à convertir.")],
    layers: Annotated[Path, typer.Option("--layers", help="Mapping YAML des calques.")],
    output: Annotated[Path, typer.Option("--output", help="GeoJSON à écrire.")],
    source_crs: Annotated[
        str, typer.Option("--source-crs", help="EPSG:3949 ou EPSG:2154.")
    ] = "EPSG:3949",
    report: Annotated[
        Path | None, typer.Option("--report", help="Rapport JSON facultatif.")
    ] = None,
    strict: Annotated[
        bool, typer.Option("--strict", help="Échouer si une anomalie est relevée.")
    ] = False,
) -> None:
    try:
        mapping = load_mapping(layers)
        result = convert_dxf(input_dxf, mapping, source_crs)
    except (ConfigError, ValueError) as error:
        typer.echo(f"Erreur de configuration : {error}", err=True)
        raise typer.Exit(2) from error

    typer.echo(format_report(result))
    if report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            json.dumps(result.report(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if not result.fatal:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result.geojson(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if result.fatal or (strict and result.issues):
        raise typer.Exit(1)
