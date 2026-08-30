from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "SHA256SUMS"
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache"}
EXCLUDED_NAMES = {"SHA256SUMS", "Composable_Assurance_CBDC_v7.bundle"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    paths = [
        path for path in ROOT.rglob("*")
        if path.is_file()
        and path.name not in EXCLUDED_NAMES
        and not any(part in EXCLUDED_PARTS for part in path.parts)
    ]
    lines = [f"{sha256(path)}  {path.relative_to(ROOT)}" for path in sorted(paths)]
    OUTPUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} checksums to {OUTPUT}")


if __name__ == "__main__":
    main()
