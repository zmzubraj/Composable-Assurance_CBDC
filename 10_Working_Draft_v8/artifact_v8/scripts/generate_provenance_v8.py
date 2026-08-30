from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "PROVENANCE_V8.json"
INCLUDED_ROOTS = ["data", "scripts", "tests", "results", "figures", "output", "docs"]
EXCLUDED_NAMES = {"PROVENANCE_V8.json"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    files = []
    for relative_root in INCLUDED_ROOTS:
        for path in sorted((ROOT / relative_root).rglob("*")):
            if path.is_file() and path.name not in EXCLUDED_NAMES and "__pycache__" not in path.parts:
                files.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)})

    packages = {}
    for distribution in [
        "numpy", "pandas", "scipy", "scikit-learn", "networkx", "matplotlib",
        "python-docx", "rapidfuzz", "Unidecode", "Faker", "cryptography", "pytest",
    ]:
        try:
            packages[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            packages[distribution] = "NOT_INSTALLED"

    manifest = {
        "schema": "cbdc-research-provenance-v8",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_boundary": (
            "Formal-model, synthetic-benchmark, official-list-snapshot, local laboratory-prototype, "
            "and queueing-digital-twin evidence. No production or national deployment claim."
        ),
        "python": sys.version,
        "platform": platform.platform(),
        "packages": packages,
        "files": files,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(MANIFEST)


if __name__ == "__main__":
    main()
