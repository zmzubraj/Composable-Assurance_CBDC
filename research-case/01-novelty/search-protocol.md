# Primary novelty-search protocol

**Protocol version:** 3  
**Cutoff:** 2026-08-29  
**Canonical builder:** `/Users/rainbow/.codex/skills/orchestrate-top-journal-research/scripts/build_prior_art_snapshot.py`  
**Builder SHA-256:** `9541ea35506a8f74bce497c71a420affc1d587e031f64df77d2254f3829746d7`  
**Coverage builder:** `build_search_coverage_v4.py`  
**Mechanical verifier:** `verify_primary_search_v4.py`  
**Source-specific arXiv repair:** `repair_arxiv_queries_v4.py`  
**Screening builder:** `build_screening_ledger_v4.py`  
**Legacy exploratory collector:** `run_primary_search.py` (retained for provenance; its pre-v4 outputs are preserved under `legacy-v1-2026-08-29/` and are not the canonical decision inputs)

## Surfaces and bounds

- OpenAlex: six exact bibliographic queries, top 25 results per query.
- Crossref: the same six queries, top 25 results per query.
- arXiv: the same six queries, top 25 results per query.
- Patents: targeted public web search plus primary Google Patents/WIPO-linked record inspection.
- Institutional/standards surface: targeted BIS, IMF, ECB, FATF, NIST, W3C, ISO and CPMI sources already present in the manuscript audit.

The canonical API run preserves exact encoded URLs and parameters, UTC timestamps, separate raw response files and SHA-256 hashes, 352 normalized records, 282 retained unique records, 70 duplicate mappings, and deterministic adapter-defined deduplication. The first arXiv capture used ungrouped multi-word strings that arXiv expanded into a broad OR expression; those superseded responses are preserved under `pre-arxiv-query-repair-2026-08-29/`. The canonical arXiv evidence now uses an exact `"central bank digital currency"` phrase plus explicit Boolean scoping for each claim axis. The query, raw and dedup JSON artifacts set `may_assert_novelty=false`. API ranking and caps make this bounded public-metadata capture, not comprehensive proof of absence.

## Query axes

1. joint/composable assurance;
2. cross-border atomicity and evidence certificates;
3. privacy and financial integrity;
4. policy limits and scale/resilience;
5. evidence maturity, prototype and validation;
6. architecture-agnostic interoperability/checkpoints.

## Screening rule

Include a record in the strongest-predecessor matrix when its title, abstract or full record overlaps at least one central novelty axis and it could materially narrow or defeat claim `C001`. Exclude generic CBDC adoption, macroeconomic or unrelated blockchain papers from the matrix while retaining them in raw/normalized retrieval evidence. Preserve preprint, patent, policy-report and publisher status. The current AI-assisted draft primary screen covers all 282 unique records and maps those decisions through the duplicate ledger to all 352 raw records. It retains 26 priority full-text candidates, 82 additional full-text candidates and 15 records requiring abstract or full-text retrieval. This does not constitute independent scientific verification; all retained candidates require accountable reconciliation before a novelty-survival decision.

## Required continuation

The first citation-chain continuation is now preserved for CEV and SSRN `5394110`: 48 Crossref and 26 OpenAlex backward records plus 24 OpenAlex forward records for CEV, and eight Crossref backward entries for SSRN `5394110`, normalized to 79 DOI-or-title-deduplicated rows. This is a title/metadata screen, not full scientific reconciliation. Before any novelty-survival decision: review the 11 retained CEV forward citations, extend chaining to any newly identified strongest predecessor, search additional patent/standards and proprietary indexes where authorized, run a differently owned independent challenge, reconcile disagreements, and refresh high-yield queries immediately before submission.
