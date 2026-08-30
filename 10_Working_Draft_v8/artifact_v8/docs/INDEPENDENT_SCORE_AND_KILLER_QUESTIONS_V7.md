# Independent score and killer-question review - v7

> **Archived v7 assessment.** Superseded for v8 by
> `TOP_JOURNAL_VALIDATION_V8.md`; its numeric scores and submission-readiness
> language must not be used as the current verdict.

## Summary score

| Assessment | Score | Verdict |
|---|---:|---|
| Overall manuscript quality | 90/100 | Strong submission-grade research manuscript |
| Architecture and problem formulation | 94/100 | Excellent compositional framing |
| Cross-border protocol | 91/100 | Strong bounded-safety design |
| Privacy and differential privacy | 90/100 | Rigorous, measurable and correctly scoped |
| AML/CFT evaluation | 85/100 | Strong predictive evidence; effectiveness remains prospective |
| Sanctions evaluation | 87/100 | Substantial calibrated laboratory evidence |
| Economic analysis | 88/100 | Strong partial-identification and adaptive-policy method |
| National-scale qualification | 86/100 | Falsifiable qualification method, not physical deployment proof |
| Reproducibility | 95/100 | Complete scripts, results, figures, checksums and claim verification |
| Top-tier journal readiness | 88/100 | Competitive submission; external institutional evidence may be requested |
| Production-deployment readiness | 70/100 | Advanced research foundation, not sovereign certification |

## Killer questions

### Does the privacy experiment establish anonymity?

**No.** It establishes measured residual linkability under synthetic learned attacks. Under generator shift, network-observer AUC falls from 0.950 under pseudonym rotation alone to 0.605 under shielding and batching, but unseen-user AUC remains 0.830. Governed real multi-PIP traces and independent red-team replication are still required.

### Is differential privacy mathematically valid?

**Yes, within the registered release boundary.** The paper defines person-level add/remove adjacency, a three-cell contribution bound, L1 sensitivity three, the Laplace mechanism and sequential composition across twelve releases. The guarantee excludes raw curator data, AML graphs, identity mappings and ad hoc queries. Sparse-cell utility remains a real limitation.

### Has AML/CFT effectiveness been demonstrated?

**Partially.** Sixteen independently generated graphs support a mean PR-AUC gain of 0.058 with a 95% bootstrap interval of 0.021-0.093 and Wilcoxon p=0.013. The effect is positive in 12/16 graphs and heterogeneous by family. FATF effectiveness still requires prospective investigator, FIU, supervisory, disruption and harm outcomes.

### Is sanctions screening operationally certified?

**No.** The benchmark uses a full official-list snapshot, disjoint positive entities, calibrated thresholds, multilingual perturbations, evidence features, prevalence-adjusted workload and ownership property tests. It lacks a live customer distribution, independent multilingual adjudication and production ownership data. At 0.01% prevalence, the balanced policy projects about 3,571 false alerts per million screenings.

### Does the economic model determine the correct holding limit?

**It determines a conditional feasible set, not a universal point.** The exposure equation makes assumptions visible, while robust optimization selects among holding, flow and remuneration policies under jurisdictional constraints. A final limit requires household microdata, bank balance sheets, funding behavior, crisis scenarios, subgroup effects and pilot observations.

### Is national-scale performance demonstrated?

**No, and the paper states this clearly.** The contribution is a qualification method: an analytical lower bound, a trace-driven queueing digital twin, an overload falsification result, physical multi-region acceptance criteria and a governed pilot gate. National scale is demonstrated only after the physical and pilot stages pass.

### Can the capacity equation guarantee sufficient hardware?

**No.** It is a necessary lower bound. Queueing, synchronization, HSM saturation, persistence, consensus, network loss and recovery must be measured together. The digital twin deliberately fails the 40,000 TPS plus region-loss scenario, showing that the framework can reject an unsafe capacity claim.

### Is cross-border split finality excluded?

**Yes under the declared model, not universally.** The 5-of-7 quorum intersection argument and state exploration exclude conflicting terminal certificates with at most two equivocating keys and durable honest locks. Dynamic membership, indefinite denial of service and post-compromise recovery require further formal and physical testing.

### Is the manuscript ready for a top journal?

**Submission-ready and competitive.** It has a clean contribution boundary, quantitative experiments, equations, 16 publication-quality figures, 22 data tables, a complete claims-to-evidence register and an accessibility-clean DOCX/PDF. The strongest systems/security venues may still require real institutional data, formal refinement and physical multi-region evidence.

### Is the architecture production-ready?

**Not yet certified.** Production requires independent cryptographic and security audits, certified HSMs, physical regions, real-data privacy/AML studies, multilingual sanctions adjudication, jurisdictional economic estimation, legal opinions and controlled central-bank pilots.
