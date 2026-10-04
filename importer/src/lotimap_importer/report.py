"""Human readable conversion diagnostics."""

from __future__ import annotations

from .models import ConversionResult


def format_report(result: ConversionResult) -> str:
    lines = [
        f"Projection source : {result.source_crs}",
        f"Entités exportées : {len(result.features)} (dont {result.lot_count} lots)",
        f"Anomalies : {len(result.issues)}",
    ]
    for issue in result.issues:
        location = " / ".join(
            part for part in (issue.layer, issue.handle) if part is not None
        )
        suffix = f" [{location}]" if location else ""
        lines.append(
            f"- {issue.severity.upper()} {issue.code}{suffix} : {issue.message}"
        )
    return "\n".join(lines)
