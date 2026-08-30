# Primary novelty-screening report

**Status:** `DRAFT_PRIMARY_SCREEN_COMPLETE`  
**Claim:** `C001`  
**Cutoff:** 2026-08-29  
**Novelty verdict:** `UNRESOLVED`  
**Scientific verification performed:** no

## Query-integrity correction

The first schema-v4 arXiv capture used ungrouped multi-word strings. The returned Atom feed showed that arXiv had expanded those strings into a broad OR expression, producing unrelated records such as atomic-physics papers. That capture remains preserved under `pre-arxiv-query-repair-2026-08-29/`, but it is no longer the canonical arXiv evidence.

`repair_arxiv_queries_v4.py` replaced only the six arXiv requests with an exact `"central bank digital currency"` phrase and explicit Boolean scoping. Crossref and OpenAlex evidence was not re-fetched or silently changed. The repaired package contains:

- 18 source-query retrievals;
- 352 raw records;
- 282 deterministic unique records;
- 70 duplicate mappings;
- six corrected arXiv requests with raw Atom responses and SHA-256 hashes.

The query-log, raw-snapshot and deduplication artifacts continue to set `may_assert_novelty=false`.

## Title/abstract screen

`build_screening_ledger_v4.py` reconstructed available abstracts from the preserved arXiv, Crossref and OpenAlex responses and generated one decision row for every unique record. The screen is explicitly AI-assisted and draft; it is not an independent scientific verdict.

| Decision | Unique records |
|---|---:|
| `PRIORITY_FULL_TEXT` | 26 |
| `INCLUDE_FULL_TEXT` | 82 |
| `RETRIEVE_ABSTRACT_OR_FULL_TEXT` | 15 |
| `EXCLUDE_GENERIC_CBDC` | 12 |
| `EXCLUDE_NO_C001_OVERLAP` | 16 |
| `EXCLUDE_OUT_OF_SCOPE` | 131 |
| **Total** | **282** |

Abstract text was available for 207 records; 75 were title-only. A title-only CBDC record is not finally excluded merely because its title lacks mechanism detail. Duplicate closure maps the 282 unique decisions back to all 352 raw records, so the coverage ledger records a draft primary-screen disposition for every captured item.

## Materially important additions

The screen added seven records to the strongest-predecessor evidence ledger and matrix:

1. Jin and Xia's peer-reviewed CEV framework (IEEE Access, DOI `10.1109/ACCESS.2022.3183092`) is the closest method-level predecessor found so far. It recommends CBDC technical solutions and verifies them with empirical experiments and formal proof. A hash-bound feature-level full-text review confirms CEV's consensus/architecture focus and compensating trade-offs versus C001's proposed six-surface non-compensating evidence ceilings; the material novelty of that decision-rule difference remains independently unverified.
2. `10.2139/ssrn.5394110` has a title that directly combines a cross-border CBDC settlement prototype, programmable compliance, ISO 20022 and FATF Travel Rule automation. Only title metadata was accessible; SSRN returned HTTP 403 during retrieval. This is a high-risk unresolved predecessor and blocks a novelty-survival decision.
3. Michalopoulos et al. (`arXiv:2509.25469`) provide an open-source offline CBDC prototype combining digital identity attestations, compliance controls, holding limits, security analysis and measured device latency.
4. Digital Co-Governance (`10.2139/ssrn.6676567`) combines multi-CBDC atomic PvP, programmable compliance, liquidity optimisation and simulation.
5. The Gold Bridge Protocol (`10.2139/ssrn.6232900`) combines atomic settlement, sanctions ring-fencing, confidential compliance and corridor simulations through a tokenised-gold bridge.
6. Bitai et al. (`10.3390/blockchains4030012`) provide a peer-reviewed analytical framework joining CBDC ledger architecture, institutional rules, a holding-cap threshold and bounded policy-rule dynamics.
7. `arXiv:2404.12821` benchmarks a privacy-preserving self-custody payment architecture with proof-of-provenance verification.

These records further defeat broad priority claims. They do not by themselves defeat the narrow C001 hypothesis, but N012 and N017 prevent a defensible `NOVELTY_SURVIVES` disposition until the missing comparisons are resolved.

## Remaining decision gates

- retrieve and inspect N012 full text or obtain an accountable access-limitation disposition;
- review the 11 retained CEV forward citations and all other retained strongest predecessors at full text where lawful access exists;
- extend backward and forward citation chaining from any newly identified strongest predecessor;
- complete patent-family, standards and authorized proprietary-index coverage;
- obtain a differently owned search challenge and reconcile disagreements;
- refresh the highest-yield searches immediately before submission.

Until those gates are satisfied, manuscript claims must stay within `C001` and the novelty verdict remains `UNRESOLVED`.
