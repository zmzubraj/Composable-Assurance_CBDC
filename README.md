# Composable assurance for sovereign digital currency (CBDC)

> **Composable assurance for sovereign digital currency (CBDC): An evidence-gated qualification framework**

Author: **Zubaer Mahmood Zubraj**
ORCID: [0009-0004-3251-3385](https://orcid.org/0009-0004-3251-3385)

**Status:** author draft (v8), not submitted and not peer reviewed.

A national digital currency must be safe, private, resistant to money laundering, final across borders and able to handle load at the same time. This work proposes a reproducible way to check those properties together rather than one module at a time, with each claim stated within its tested scope.

## Start here

- **Paper (v8 author draft):** [`10_Working_Draft_v8/artifact_v8/output/Composable_Assurance_CBDC_Author_Draft_v8.pdf`](10_Working_Draft_v8/artifact_v8/output/Composable_Assurance_CBDC_Author_Draft_v8.pdf)
- **Code, data and how to reproduce:** [`10_Working_Draft_v8/artifact_v8/README.md`](10_Working_Draft_v8/artifact_v8/README.md) (`RUN_ALL.sh`, `VERIFY.sh`)
- **Claims and their evidence:** [`10_Working_Draft_v8/artifact_v8/docs/COMPLETION_EVIDENCE_MATRIX_V8.md`](10_Working_Draft_v8/artifact_v8/docs/COMPLETION_EVIDENCE_MATRIX_V8.md)

## What the evidence covers

| Claim | Evidence type |
|---|---|
| Cross-border settlement cannot end in two conflicting outcomes | Exhaustive enumeration of 2,013 states in a custom Python model |
| The prototype enforces freshness, quorum and ledger rules | Local lab test (11 services, 5-of-7 quorum) |
| Shielding and batching reduce but do not remove linkability | Simulation |
| Person-level differential privacy has a bounded budget | Simulation |
| Cross-institution features improve AML ranking | Synthetic transaction graphs |
| Sanctions screening trade-off on the official OFAC list | Internal benchmark |
| There is no universal holding limit | Analytic |
| Scale must be proven in stages | Simulated load scenarios |

These are bounded developmental checks (14/14 tests pass in the artefact). They are not field validation, production approval or national-scale deployment, and novelty against closely related frameworks is not yet independently assessed.

## Repository layout

- `10_Working_Draft_v8/artifact_v8/`: current paper, code, data, figures, results and tests
- `01_Manuscript/`, `04_Figures/`, `05_Supplementary/`, `06_Reproducibility/`, `07_Declarations/`, `08_Editorial_Materials/`: the earlier v7 package, kept for reference

## Licence

Code and repository tooling: [MIT License](LICENSE), copyright (c) 2026 Zubaer Mahmood Zubraj. Manuscript and original figures: see [`CONTENT_LICENSE.md`](10_Working_Draft_v8/artifact_v8/CONTENT_LICENSE.md). Third-party sources and datasets keep their original terms.
