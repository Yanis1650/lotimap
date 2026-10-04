from pathlib import Path

import pytest

from lotimap_importer.config import LayerMapping, load_mapping

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "data" / "demo" / "dxf"
MAPPING = ROOT / "importer" / "config" / "layers.example.yaml"


@pytest.fixture
def layers() -> LayerMapping:
    return load_mapping(MAPPING)
