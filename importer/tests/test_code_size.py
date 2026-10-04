"""Keep the project's hand-written code within its agreed size limit."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".vue",
    ".sh",
    ".ps1",
    ".css",
    ".scss",
    ".html",
    ".sql",
}
CODE_FILENAMES = {"Dockerfile"}
SKIP_DIRS = {".venv", "node_modules", ".nuxt", ".output", "__pycache__"}


def test_code_files_have_at_most_200_lines() -> None:
    oversized = []
    for folder in ("samples", "importer", "enrichment", "web", "deploy"):
        for directory, subdirectories, filenames in os.walk(ROOT / folder):
            subdirectories[:] = [
                name for name in subdirectories if name not in SKIP_DIRS
            ]
            for filename in filenames:
                path = Path(directory) / filename
                if path.suffix not in CODE_SUFFIXES and path.name not in CODE_FILENAMES:
                    continue
                with path.open(encoding="utf-8") as source:
                    line_count = sum(1 for _ in source)
                if line_count > 200:
                    oversized.append(f"{path.relative_to(ROOT)}: {line_count} lignes")
    assert not oversized, "Fichiers de code trop longs : " + ", ".join(oversized)
