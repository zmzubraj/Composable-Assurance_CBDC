# CEV full-text feature reconciliation

**Review date:** 2026-08-29  
**Seed:** Jin and Xia, *CEV Framework*, IEEE Access 10 (2022), 63698-63714  
**DOI:** `10.1109/ACCESS.2022.3183092`  
**Public full text:** arXiv `2112.01122v3`, 16 PDF pages  
**PDF SHA-256:** `a8c770974c6510e8d9fe55f33ebc8a1bab87b569eca6fd769d04b01e6d7b0fb4`  
**Extracted text SHA-256:** `baf6a67bd35168c985d2cd8531b193b25b329ef6ce19c31378e91c550e60e4a4`

## Decision-bearing result

CEV is a genuine method-level predecessor, not merely a related architecture paper. It already combines an evaluation sub-framework with a verification sub-framework, recommends consensus/operating-architecture solutions, tests performance empirically, and uses formal arguments for security and privacy. It therefore defeats any statement that this manuscript is the first CBDC evaluation framework, first CBDC verification framework, or first framework to combine empirical and formal CBDC assessment.

The reviewed full text also supports a narrower, still-unverified distinction. CEV explicitly permits architecture to compensate for weak consensus features and iterates preferences until an acceptable balance point. Claim `C001` instead proposes non-compensating evidence ceilings: failure on a critical assurance surface blocks or narrows the affected claim regardless of strength elsewhere. CEV declares performance, security and privacy as its three technical feature families and leaves additional features to future work; the reviewed version does not evaluate AML/sanctions, differential privacy, adaptive holding-limit inference, cross-border terminal evidence certificates, or a staged physical-to-field scale gate.

This is not a positive novelty verdict. Breadth, packaging and terminology alone are insufficient. The materiality of the non-compensating decision rule still requires independent challenge, reconciliation of later papers that cite CEV, and comparison with the inaccessible high-overlap SSRN `5394110` full text.

## Audit method and limits

- Reviewed all 16 pages of the public arXiv v3 PDF and a layout-preserving `pdftotext` extraction.
- Searched the complete text for AML, sanctions, compliance, differential privacy, holding limits, evidence maturity, deployment, field evidence, legal finality and cross-border terms.
- Used affirmative full-text passages for CEV's declared scope and methods. Term absence is recorded only as “not found in this reviewed version,” never as proof of universal absence.
- The feature-by-feature record is preserved in `cev-feature-reconciliation.csv`.
- This is a primary integration-owner review, not the differently owned independent novelty challenge.

## Current disposition

`C001 = NOVELTY_UNRESOLVED`. CEV no longer blocks feature-level reconciliation itself, but it remains the closest method predecessor. The open blockers are retained forward-citation full-text review, SSRN `5394110` retrieval or justified inaccessible-source disposition, patent/standards expansion, independent challenge and submission-time refresh.
