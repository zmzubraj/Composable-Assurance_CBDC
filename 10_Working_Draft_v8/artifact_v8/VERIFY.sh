#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -f SHA256SUMS ]]; then sha256sum -c SHA256SUMS; fi
"$PYTHON_BIN" -m pytest
"$PYTHON_BIN" -O scripts/verify_v8.py
"$PYTHON_BIN" -O scripts/verify_jfmi_v8.py
