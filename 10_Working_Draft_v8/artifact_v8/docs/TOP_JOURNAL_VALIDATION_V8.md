# Manuscript killer-question and publication-readiness audit - v8

**Assessment date:** 29 August 2026  
**Manuscript:** `Composable_Assurance_CBDC_Author_Draft_v8`  
**Article state:** journal-neutral author draft  
**Target venue:** not yet selected  
**Evidence maturity:** bounded formal model, synthetic evaluation, laboratory prototype, official-list snapshot, analytical economics, and queueing simulation

## Overall judgment

**Supported developmental stage: TECHNICALLY PROMISING.**

The manuscript and artifact form a coherent, executable research package, and the central claims are mostly proportional to the evidence. It is not yet defensible to call the package `FIELD-JOURNAL READY` or `TOP-JOURNAL CASE PLAUSIBLE`: the target venue is unresolved; a canonical, hash-bound schema-v4 primary novelty-search package now includes an AI-assisted title/abstract screen, priority-candidate reconciliation, a full-text CEV comparison and a 79-row citation-chain snapshot, but retained forward-citation/full-text review, broader coverage and a differently owned independent challenge remain incomplete; all behavioral data are synthetic; scale evidence is simulated rather than physical; and accountable author/declaration/submission fields are open.

No fatal scientific defect was identified in the bounded author-draft claim. The main risk is claim drift: any wording that turns the qualification pathway into proof of operational AML effectiveness, anonymity, universal policy optimality, production safety, or national capacity would exceed the available evidence.

## Claim map

| Claim ID | Manuscript claim | Direct support | Maturity ceiling | Audit result |
|---|---|---|---|---|
| C1 | Quorum-certified cross-border conversion excludes conflicting terminal outcomes under declared assumptions. | Formal state exploration: 2,013 states, 19,480 transitions, zero bounded violations. | V1 ANALYTIC | PASS within model boundary |
| C2 | The minimum prototype enforces quote/policy freshness, quorum consistency, and ledger invariants. | Eleven local services, 84 transfers, rejection tests, 14-test suite. | V3 INTERNAL | PASS |
| C3 | Shielding and batching reduce but do not eliminate transaction linkability. | Synthetic learned attacks: network AUC 0.605 under generator shift; unseen-user AUC 0.830. | V2 SIMULATED | PASS |
| C4 | The registered aggregate release has a bounded differential-privacy budget. | Person-level adjacency, sensitivity 3, twelve-release ledger, epsilon example 4, enforcement test. | V2 SIMULATED | PASS within release boundary |
| C5 | Cross-institution features improve synthetic AML ranking on average, heterogeneously. | Sixteen graphs; delta PR-AUC 0.05797; 95% bootstrap CI 0.02084-0.09252; p=0.01309; 12/16 positive. | V2 SIMULATED | PASS |
| C6 | The sanctions policy exposes an explicit recall/false-positive/workload trade-off on an archived official-list benchmark. | 19,178 records, 20,010 aliases, recall 0.873846, FPR 0.003571, ownership tests 500/500. | V3 INTERNAL | PASS within benchmark scope |
| C7 | A universal holding-limit optimum is unsupported; policy selection must be conditional. | Exposure model, robust optimization, scenario envelope, illustrative 5% value. | V1 ANALYTIC | PASS |
| C8 | National-scale readiness should be falsified through staged qualification rather than inferred from a capacity equation. | Necessary lower bound, seven-scenario digital twin, overload failure at p99 8,432 ms, physical/pilot gates. | V2 SIMULATED | PASS as a method; not as capacity proof |

## Killer-question ledger

| Question group | Status | Evidence and manuscript location | Consequence / smallest adequate action |
|---|---|---|---|
| Is there one coherent central contribution? | PARTIAL | Abstract, introduction, contribution map, and discussion frame a joint qualification method; the manuscript still spans six technical domains. | Make the claim-to-evidence qualification method the explicit organizing spine in the venue-specific revision. |
| Is the problem significant and decision-relevant? | PASS | The paper addresses settlement safety, privacy, financial integrity, monetary control, and scale claims that must coexist in sovereign systems. | Preserve concrete governance consequences; avoid generic CBDC advocacy. |
| Is the contribution materially distinct from the strongest known predecessors? | PARTIAL | The repaired schema-v4 primary search preserves 18 source-query retrievals, 352 raw records, 282 unique records, 70 duplicates, a 282-record draft screen, 26 reconciled priority candidates, 17 claim-linked evidence/matrix rows, an 11-feature CEV full-text comparison and a 79-row citation-chain snapshot. | Review the 11 retained CEV forward citations, resolve or explicitly disposition the inaccessible SSRN full text, expand patent/standards coverage and complete a differently owned challenge before any positive novelty decision. |
| Is novelty overstated as the first isolated component? | PASS | v8 explicitly rejects first-component framing and limits the difference to the joint qualification method. | Keep this wording stable through title, abstract, highlights, and cover letter. |
| Could a close predecessor defeat the central claim? | UNKNOWN | CEV already defeats any broad first CBDC evaluation/verification-framework claim; SSRN 5394110 remains a high-risk title-level cross-border prototype candidate whose full text was unavailable, and the narrower joint-method claim has not received an independent challenge. | Treat novelty as `UNRESOLVED` until retained-candidate full-text review, citation chaining, independent reconciliation and the submission-time refresh pass. |
| Are formal claims tied to explicit assumptions? | PASS | Quorum size, fault bound, honest-lock durability, and explored state boundary are stated. | Do not generalize to dynamic membership, recovery, or unrestricted liveness. |
| Does the formal model refine to the prototype? | PARTIAL | `FORMAL_MODEL_TO_PROTOTYPE_MAPPING_V8.md` now traces each bounded property through model, implementation, tests and results, while explicitly stating that no mechanically proved refinement relation exists. | Pursue formal refinement only if the confirmed target venue expects it; do not call traceability a proof. |
| Can the prototype be reproduced without hidden services? | PASS | Localhost-only services, checked-in code, locked Python 3.12 environment, deterministic controls, and tests are present. | Publish the exact release artifact and DOI after approval. |
| Does the privacy result establish anonymity? | PASS as a negative boundary | Results show residual attack performance, including unseen-user AUC 0.830, and do not claim anonymity. | Preserve attacker model, generator shift, cohort caveats, and residual leakage. |
| Is the differential-privacy unit and adjacency relation unambiguous? | PASS | Person-level add/remove adjacency and a three-cell contribution bound are specified. | Ensure every released table is mapped to the accountant; exclude ad-hoc queries. |
| Does the DP guarantee cover identity, AML, or raw curator data? | PASS as excluded | The manuscript excludes these surfaces. | Prevent future prose from implying system-wide privacy. |
| Does the AML analysis prove regulatory effectiveness? | PASS as excluded | The paper reports predictive ranking on synthetic graphs and separates FATF effectiveness outcomes. | Keep investigator, FIU, disruption, and harm claims prospective. |
| Are AML uncertainty and heterogeneity visible? | PASS | Effect size, bootstrap interval, Wilcoxon test, and 12/16 positive graph count are reported. | Add family-level ablation/baseline details if a venue requests deeper ML evaluation. |
| Is sanctions evaluation free from train/test entity leakage? | PASS | Positive entities are disjoint and generated query populations are held out. | Preserve split-generation code and hashes. |
| Does sanctions performance translate directly to operational workload? | PARTIAL | Prevalence-adjusted workload is modeled, but no live customer distribution or independent adjudication exists. | Keep operational language conditional and add governed institution data only under a new approved protocol. |
| Is the holding limit a universal recommendation? | PASS as excluded | The analysis explicitly rejects a universal optimum and labels EUR 1,643.49 illustrative. | Preserve units, scenario inputs, and conditionality. |
| Does the scale model prove national throughput? | PASS as excluded | The digital twin deliberately fails one overload case and the paper says national scale is not demonstrated. | Do not replace physical multi-region qualification with simulation. |
| Are endpoints, denominators, units, and thresholds visible? | PASS | Results and editable tables report AUC/PR-AUC, records, aliases, graph count, transfer count, latency, scenario load, and boundaries. | Recheck final-size tables after venue formatting. |
| Are exploratory and confirmatory roles separated? | PARTIAL | Metrics and thresholds are explicit, but the package was developed iteratively and lacks a frozen preregistered confirmatory protocol. | Label current work developmental; preregister only materially new confirmatory studies. |
| Are multiplicity and model-selection risks controlled? | PARTIAL | `ANALYSIS_ROLE_AND_DEVIATIONS_V8.md` classifies each evidence family, prevents cross-domain p-value aggregation and records the absence of preregistration. | Any stronger confirmatory study requires a prospectively frozen protocol; current evidence remains developmental. |
| Are negative results and boundary failures preserved? | PASS | Residual privacy linkage, heterogeneous AML gains, no universal economic optimum, and overload failure are reported. | Keep them prominent in abstract/discussion/limitations. |
| Are data origins and authorization labels explicit? | PASS | Synthetic privacy/AML generation, archived OFAC inputs, analytical anchors, and simulated load are documented. | No relabeling as participant, customer, institutional, or field evidence. |
| Are all central results executable from source? | PASS locally | `RUN_ALL.sh`, locked dependencies, source data/code, tests, figure/manuscript builders, provenance, and checksums are present. | Re-run in an isolated release environment and archive logs for the final submission tag. |
| Are figures and tables editable, traceable, and legible? | PASS locally | Source figures/tables and machine-readable results are present; the 17-page PDFs were inspected, with remediated Figures 2, 3 and 14 rechecked at native source size and manuscript scale (`VISUAL_QA_V8.md`). | Repeat final-size visual QA after venue reformatting and check grayscale/color-vision accessibility. |
| Are citations complete and claim-matched? | PASS for current draft | All 44 bibliography entries are cited; CEV is now included as the closest method-level predecessor and broad first-framework language is excluded. | Run DOI/URL and bibliography-style validation after venue conversion; reconcile retained candidates before submission. |
| Are reporting and ethics statements sufficient? | PARTIAL | Current work uses no participants/customer data; evidence boundaries and availability are present, but author-approved declarations are incomplete. | Add ethics determination, funding, conflicts, CRediT, AI-use, data/code, and license statements as applicable. |
| Is the article compliant with a current target venue? | UNKNOWN | No primary journal or article type is selected. | Verify official instructions on the date of adaptation and complete the actual checklist. |
| Is the manuscript anonymous where required? | UNKNOWN | Journal-neutral author draft omits final identity package, but target double-anonymization rules are unknown. | Create separate blinded manuscript and title page only after venue confirmation. |
| Can an editor verify the main contribution quickly? | PARTIAL | Abstract gives quantitative evidence, but breadth may obscure the single methodological contribution. | Use venue-specific key messages and a one-page contribution/evidence schematic. |
| Are real-world, generality, and deployment claims proportionate? | PASS | The manuscript states formal/synthetic/lab/simulation scope and excludes production/national proof. | Any new operational claim must be supported by matching V4/V5 evidence. |
| Does a clean build prove scientific validity? | PASS as rejected | Verification is presented as mechanical/reproducibility evidence, not scientific certification. | Keep gate judgments separate from build status. |
| Is accountable submission approval present? | UNKNOWN | No author identities, final declarations, portal preview, or submission authorization are recorded. | Human authors approve the final rendered files and portal data. |

## Strongest-prior-art novelty matrix

| Predecessor | Strongest overlap | Material difference claimed by v8 | Residual uncertainty |
|---|---|---|---|
| Lee et al. (2021), atomic cross-chain settlement | Atomicity and cross-ledger settlement safety | v8 connects bounded settlement evidence to privacy, financial integrity, policy, and staged scale qualification. | Other atomic-swap and interoperability protocols may narrow the settlement contribution. |
| CBDC-AquaSphere (2023) | Multi-ledger CBDC architecture and privacy/scalability objectives | v8 centers claim maturity and executable qualification across several assurance surfaces. | Preprint and follow-on literature require citation chaining. |
| IMF Cross-Border Payments with Retail CBDCs (2024) | Five-element cross-border design framework | v8 supplies executable formal/prototype/evaluation gates rather than only policy architecture. | Adjacent IMF/BIS implementations may add closer empirical precedents. |
| BIS CGIDE functional CBDC architecture (2024) | Functional requirements and system architecture | v8 binds architecture elements to falsifiable evidence ceilings and rejection gates. | Standards and central-bank technical reports require broader search coverage. |
| Pocher and Veneris (2022) | Privacy and AML regulation-by-design | v8 evaluates residual privacy leakage, bounded DP releases, AML ranking, sanctions workload, economics, and scale jointly. | Later privacy-preserving compliance systems may provide closer joint evidence. |
| Project Agorá (updated 2026) | Controlled real-value programmable cross-border wholesale experiment | v8 is a research qualification method for independent sovereign ledgers and explicitly lacks field maturity. | Agorá is stronger real-value evidence on a narrower operational surface and must not be portrayed as weaker overall. |
| Bharathan and Pillai (2022) | Composable standards-based CBDC implementation with software demonstrations | v8 does not claim first composability; it hypothesizes a non-compensating cross-surface qualification method. | Full-text feature reconciliation and citation chaining remain incomplete. |
| WIPO WO2025085074A1 (2025) | Architecture-agnostic reservation, message, checkpoint and finalization flow | v8 does not claim first architecture-agnostic interoperability; it binds compliance, FX and evidence-maturity gates to a narrower method claim. | Patent-family and cited-patent chaining remain incomplete; legal status is not a legal conclusion. |
| Michalopoulos et al. (2025) | Offline CBDC privacy and compliance design options | v8 covers a broader online multi-surface qualification package rather than first privacy/compliance-by-design. | Offline behavior is not evaluated by v8 and related citation chains remain incomplete. |
| Bernardo et al. (2025) | Formal validation for offline-CBDC operational resilience | v8 executes a bounded model and staged scale falsification, but claims no refinement proof. | Preprint status, offline scope and missing formal refinement limit comparison. |
| Jin and Xia (2022), CEV framework | CBDC evaluation and verification using consensus/operating-architecture recommendations, experiments and formal analysis | v8 does not claim the first CBDC evaluation framework; its narrower hypothesis is a non-compensating maturity ceiling across settlement, privacy, integrity, policy and scale evidence. | Feature-level full-text reconciliation is complete and confirms a decision-rule difference; 11 retained forward citations and an independent materiality challenge remain before the narrower novelty claim can survive. |
| SSRN 5394110 (2025) | Cross-border CBDC settlement prototype with programmable compliance, ISO 20022 and FATF Travel Rule automation | v8 additionally combines formal settlement checks, privacy/DP, AML/sanctions workload, holding limits and scale falsification under an evidence ceiling. | Only title-level metadata was accessible; the unavailable full text is a novelty-survival blocker, not evidence of difference. |

**Novelty disposition:** `UNRESOLVED`, with a potentially differentiating joint qualification method. The current bibliography is improved and plausible, but a bounded current search cannot prove universal novelty.

## Fatal-flaw and stop-condition audit

No current fatal flaw requires withdrawing the bounded author draft. The following become blocking if introduced or left unresolved at the corresponding stage:

1. **Claim escalation:** describing synthetic/internal evidence as operational effectiveness, anonymity, production safety, field impact, or national capacity.
2. **Defeated novelty:** a predecessor that already supplies the same joint claim-to-evidence qualification method with equal or stronger evidence.
3. **Irreproducible central result:** failure of the locked build, tests, provenance, source-data chain, or result-to-manuscript verification.
4. **Unresolved authorship/ethics/integrity issue:** missing accountable author approval, undisclosed conflicts/funding/AI use, or misrepresented data provenance.
5. **Venue noncompliance:** page/word, anonymity, declaration, reference, data/code, or submission requirements not satisfied for the selected journal.

## Simulated editor and reviewer objections

| Objection | Severity | Current answer | Required strengthening |
|---|---|---|---|
| “This is six papers compressed into one.” | Major | One qualification method and maturity boundary connect all modules. | Tighten the contribution spine; move implementation detail to supplement if venue length requires it. |
| “Most evaluation is synthetic, so practical significance is unknown.” | Major | The paper labels evidence maturity and does not claim field effectiveness. | Retain bounded claims; add external/field evidence only through a separately approved protocol. |
| “The formal model is not a proof of the implementation.” | Major | The bounded model, prototype, tests and results are now linked in `FORMAL_MODEL_TO_PROTOTYPE_MAPPING_V8.md`; the lack of refinement proof is explicit. | Preserve this boundary; add formal refinement only if justified by venue scope. |
| “Privacy and AML metrics are vulnerable to generator artifacts.” | Major | Generator shift and unseen-user attacks expose residual leakage; AML uses 16 independent graphs and uncertainty. | Add alternate generators, stronger baselines, and preregistered external data if stronger generality is claimed. |
| “The sanctions FPR is operationally expensive.” | Major but useful | Workload is prevalence-adjusted and explicitly reported. | Keep analyst-capacity and harm trade-offs central; avoid one-threshold recommendations. |
| “National-scale language is premature.” | Major if overstated | The scale contribution is a falsification pathway and includes an overload failure. | Preserve `not demonstrated` wording in title/abstract/conclusion and venue highlights. |
| “Novelty is a synthesis rather than a new primitive.” | Major | v8 claims a joint qualification method, not first invention of isolated primitives. | Complete the reproducible strongest-prior-art search and articulate why the integration changes assurance decisions. |

## Prioritized remediation

### P1 - required before venue-specific submission certification

1. Confirm one primary target journal, article type, and dated official requirements.
2. Freeze the six-field research intake and canonical claim boundary.
3. Complete full-text review of the 11 retained CEV forward citations and other strongest candidates, obtain SSRN 5394110 or preserve a justified access-limit disposition, extend citation chains as needed, expand patent/standards coverage, run a differently owned challenge and refresh searches at submission time.
4. Preserve and revalidate the completed model-to-prototype mapping and analysis-role/deviation ledger after any material code or claim change.
5. Apply the selected venue's structure, length, reference, anonymity, declaration, data/code, supplement, and checklist rules.

### P2 - required before accountable submission approval

1. Add verified author names, affiliations, corresponding-author details, CRediT roles, funding, conflicts, ethics determination, AI-use disclosure, data/code availability, and license.
2. Archive the exact release and assign a repository URL/DOI if the authors approve public release.
3. Re-run isolated reproduction, reference/DOI validation, final-size visual QA, accessibility checks, checksum verification, and rendered PDF/portal review.

### P3 - valuable for a stronger later revision

1. Add alternate-generator and ablation evidence for privacy/AML sensitivity.
2. Add physical multi-region and governed external validation only if the intended claims require them and all approvals/access gates pass.
3. Update the manuscript from later technical or methodological feedback without representing unperformed review as completed evidence.

## Validation stage and forecast

- **Current stage:** `TECHNICALLY PROMISING`
- **Target-venue acceptance forecast:** `NOT ESTIMABLE` because no journal/article type or target-matched calibration dataset is fixed.
- **External acceptance:** not claimed; only a verified editorial decision could establish it.
- **Next reassessment:** after target-journal selection, independent novelty-search completion and reconciliation, and venue-specific manuscript build.

## Source and artifact ledger

- Author draft: `output/Composable_Assurance_CBDC_Author_Draft_v8.docx` and `.pdf`
- Claim/evidence data: `results/`, source tables, and manuscript builder
- Citation validation: `docs/CITATION_AUDIT_V8.md`
- Feasibility gate: `docs/FEASIBILITY_GATE_V8.md`
- Mechanical verification: `docs/VERIFICATION_V8.json`
- Provenance: `docs/PROVENANCE_V8.json`
- Reproduction: `RUN_ALL.sh`, `VERIFY.sh`, `uv.lock`, `requirements.txt`, `tests/`
- Package integrity: `SHA256SUMS`

This audit is developmental quality assurance. It does not replace qualified human authors, institutional determinations, peer review, or an editorial decision.
