# Composable Assurance for Sovereign Digital Currency - author draft v8

This reproducibility package supports the manuscript:

**Composable assurance for sovereign digital currency (CBDC): An evidence-gated qualification framework**

## Evidence boundary

The package reports formal-model, synthetic-benchmark, laboratory-prototype and queueing-digital-twin evidence. It does not claim a national CBDC deployment, production-certified cryptography, operational FATF effectiveness or a universal monetary-policy limit.

## Main files

- `output/Composable_Assurance_CBDC_Author_Draft_v8.docx`
- `output/Composable_Assurance_CBDC_Author_Draft_v8.pdf`
- `scripts/` - experiment, figure, manuscript and verification source
- `results/` - machine-readable result tables and summaries
- `figures/` - manuscript diagrams and charts
- `data/` - archived OFAC inputs used by the sanctions benchmark
- `tests/` - executable invariant, tamper-rejection and model-boundary tests
- `docs/VERIFICATION_V8.json`
- `docs/PROVENANCE_V8.json`
- `docs/FEASIBILITY_GATE_V8.md`
- `docs/TOP_JOURNAL_VALIDATION_V8.md`
- `docs/FORMAL_MODEL_TO_PROTOTYPE_MAPPING_V8.md`
- `docs/ANALYSIS_ROLE_AND_DEVIATIONS_V8.md`
- `docs/CITATION_AUDIT_V8.md`
- `docs/JFMI_COMPLIANCE_V8.md`
- `docs/JFMI_VERIFICATION_V8.json`
- `docs/JFMI_SUBMISSION_INVENTORY_V8.json`
- `docs/AUTHOR_DECISION_SHEET_V8.md`
- `../../research-case/01-novelty/` - canonical schema-v4 primary novelty-search evidence and fail-closed unresolved challenge disposition
- `docs/a11y_audit_v7.json`
- `LICENSE-CODE-MIT.txt` - MIT licence for original software/code
- `CONTENT_LICENSE.md` - separately gated manuscript/figure content licence

## Reproduction

The preferred route uses Python 3.12 and the checked-in `uv.lock`:

```bash
UV_PROJECT_ENVIRONMENT=../.venv uv sync --frozen
PYTHON_BIN=../.venv/bin/python ./RUN_ALL.sh
PYTHON_BIN=../.venv/bin/python ./VERIFY.sh
```

Alternatively, create a Python 3.12 environment, install the exact versions in
`requirements.txt`, and run the same scripts with `PYTHON_BIN` pointing to that
environment.

The build sets a deterministic Python hash seed, non-interactive plotting backend,
UTC timezone and C locale. It executes tests before experiments, renders the author
draft to DOCX/PDF, verifies claims under `python -O`, records provenance, and writes
the package checksums.

The sanctions pipeline first generates the entity-disjoint scored benchmark through
`sanctions_v6.py`, then calibrates the v7 policy frontier through `sanctions_v7.py`.

## Author-draft boundary

The v8 author draft is journal-neutral. Venue-specific ordering, reference style,
title-page metadata, declarations, repository/DOI details and portal fields are
completed only after the target journal and accountable author information are
confirmed.

The current evidence-gated developmental stage is `TECHNICALLY PROMISING`. The
bounded author-draft path is supported mechanically. A canonical primary novelty-search
package is now hash-bound in the schema-v4 research case. Its repaired 18-query search
contains 352 raw and 282 unique records, a complete draft title/abstract screen, 26
reconciled priority candidates, a hash-bound CEV full-text comparison and a 79-row
deduplicated backward/forward citation-chain snapshot. Review of the 11 retained CEV
forward citations, the inaccessible SSRN 5394110 full text or access disposition,
broader patent/standards coverage, a differently owned challenge and submission-time
refresh remain open, alongside target-venue confirmation, author declarations and
human submission approval.

## Provisional JFMI trial package

JFMI is a trial target, not yet the confirmed final journal. The reversible package in
`output/jfmi_provisional/` contains a blinded manuscript, a separate gated title-page
template, a figure/table legends file, and sixteen editable SVG figures. Confirmed
author metadata is recorded separately from the blinded manuscript. Affiliation,
postal address, corresponding-author designation, conflict statement, AI-use wording,
public deposit/DOI, final venue and submission approval remain explicit gates.
An optional cover-letter template is also generated; the checked JFMI instructions do
not list it as mandatory. The author has deferred the remaining identity, conflict and
AI wording fields for later manual entry, so the automated inventory remains fail-closed.

## Commands

```bash
./RUN_ALL.sh
./VERIFY.sh
```

## Required external gates

National deployment claims require physical multi-region execution, certified HSMs, realistic PIP workloads, independent security and legal audits, governed real-data privacy/AML studies, live multilingual sanctions adjudication, jurisdiction-specific economic estimation and controlled pilots.
