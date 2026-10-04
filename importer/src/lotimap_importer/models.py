"""Small data structures shared by the conversion steps."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from shapely.geometry import Point, Polygon


@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    severity: Literal["warning", "error"] = "warning"
    layer: str | None = None
    handle: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


@dataclass(frozen=True)
class NumberText:
    value: str
    point: Point
    layer: str
    handle: str


@dataclass
class Lot:
    polygon: Polygon
    layer: str
    handle: str
    numbers: list[NumberText] = field(default_factory=list)


@dataclass
class ConversionResult:
    source_crs: str
    features: list[dict[str, Any]] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    fatal: bool = False

    @property
    def lot_count(self) -> int:
        return sum(feature["properties"]["kind"] == "lot" for feature in self.features)

    def geojson(self) -> dict[str, Any]:
        return {
            "type": "FeatureCollection",
            "features": self.features,
            "metadata": {"source_crs": self.source_crs, "area_unit": "m2"},
        }

    def report(self) -> dict[str, Any]:
        return {
            "source_crs": self.source_crs,
            "feature_count": len(self.features),
            "lot_count": self.lot_count,
            "issue_count": len(self.issues),
            "fatal": self.fatal,
            "issues": [issue.to_dict() for issue in self.issues],
        }
