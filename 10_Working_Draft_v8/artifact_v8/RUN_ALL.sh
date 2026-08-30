#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PROJECT_PYTHON="$ROOT/../.venv/bin/python"
if [[ -z "${PYTHON_BIN:-}" && -x "$PROJECT_PYTHON" ]]; then
  PYTHON_BIN="$PROJECT_PYTHON"
else
  PYTHON_BIN="${PYTHON_BIN:-python3}"
fi
export MPLBACKEND=Agg
export PYTHONHASHSEED=0
export LC_ALL=C
export LANG=C
export TZ=UTC

"$PYTHON_BIN" -m pytest
"$PYTHON_BIN" scripts/cross_border_model_v5.py
"$PYTHON_BIN" scripts/cross_border_bft_v5.py
"$PYTHON_BIN" scripts/privacy_v7.py
"$PYTHON_BIN" scripts/aml_v7.py
"$PYTHON_BIN" scripts/sanctions_v6.py
"$PYTHON_BIN" scripts/sanctions_v7.py
"$PYTHON_BIN" scripts/economic_v7.py
"$PYTHON_BIN" scripts/performance_v7.py
"$PYTHON_BIN" scripts/make_diagrams_v7.py
"$PYTHON_BIN" scripts/build_manuscript_v8.py

if command -v soffice >/dev/null 2>&1; then
  soffice --headless --convert-to pdf --outdir output output/Composable_Assurance_CBDC_Author_Draft_v8.docx >/dev/null
else
  echo "soffice is required to build the PDF" >&2
  exit 1
fi

"$PYTHON_BIN" scripts/build_jfmi_submission_v8.py
soffice --headless --convert-to pdf --outdir output/jfmi_provisional \
  output/jfmi_provisional/Composable_Assurance_CBDC_JFMI_Blinded_Manuscript_v8.docx \
  output/jfmi_provisional/Composable_Assurance_CBDC_JFMI_Title_Page_TEMPLATE_v8.docx \
  output/jfmi_provisional/Composable_Assurance_CBDC_JFMI_Figure_Table_Legends_v8.docx \
  output/jfmi_provisional/Composable_Assurance_CBDC_JFMI_Cover_Letter_TEMPLATE_v8.docx >/dev/null

"$PYTHON_BIN" -O scripts/verify_v8.py
"$PYTHON_BIN" -O scripts/verify_jfmi_v8.py
"$PYTHON_BIN" scripts/generate_provenance_v8.py
"$PYTHON_BIN" scripts/generate_checksums_v8.py
sha256sum -c SHA256SUMS
