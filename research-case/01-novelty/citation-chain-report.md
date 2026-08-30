# Backward and forward citation-chain report

**Cutoff:** 2026-08-29  
**Seeds:** CEV (`10.1109/ACCESS.2022.3183092`) and SSRN 5394110 (`10.2139/ssrn.5394110`)  
**Machine-readable outputs:** `citation-chain-ledger.csv`, `citation-chain-summary.json`  
**Builder:** `build_citation_chains_v4.py`  
**Test:** `test_build_citation_chains_v4.py`

## Captured evidence

- CEV: 48 Crossref reference entries, 26 of 35 OpenAlex referenced works with public metadata, and 24 OpenAlex forward-citation records.
- SSRN 5394110: eight Crossref reference entries; OpenAlex reports zero referenced works and zero forward citations. Crossref has no abstract. These metadata do not substitute for its unavailable full text.
- After deterministic DOI-or-title deduplication, the ledger contains 79 rows.
- The CEV forward set contains 11 CBDC-title citations retained for later full-text reconciliation and 13 non-CBDC title matches excluded as likely citation noise. The excluded set includes an obviously unrelated eco-cement paper, demonstrating why citation indexes cannot be accepted without screening.
- SSRN 5394110's reference list confirms antecedent reliance on Project mBridge, Project Dunbar, FATF risk-based guidance, ISO 20022 migration material, Travel Rule interoperability and CBDC anonymity work. This makes the title-level overlap more credible but still does not reveal the paper's actual method or results.

## Scientific boundary

This is an auditable public-metadata citation-chain snapshot. It does not establish claim support, citation context, full-text overlap, independent verification or novelty. OpenAlex returned only 26 of CEV's 35 referenced-work identifiers with public metadata; Crossref entries vary in completeness; and the forward screen is title-only. `scientific_verification_performed=false`, `independent_challenge_performed=false`, and the novelty verdict remains `UNRESOLVED`.

## Required continuation

1. Review the 11 retained CEV forward citations that can materially reinterpret or extend the framework.
2. Continue lawful public retrieval for SSRN 5394110; if it remains inaccessible, preserve an explicit access-limit disposition and do not infer difference.
3. Reconcile any closer method or cross-border prototype into the evidence ledger and manuscript.
4. Run the differently owned independent challenge and submission-time refresh before any novelty-survival verdict.
