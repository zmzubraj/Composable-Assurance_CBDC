# Analysis roles and deviations — v8

**Date:** 2026-08-29  
**Scope:** The quantitative and executable evidence carried by the v8 manuscript.

## Role classification

| Evidence family | Analysis role | Frozen decision or contrast | Uncertainty / diagnostic treatment | Deviation status | Claim ceiling |
|---|---|---|---|---|---|
| Cross-border state model | Bounded confirmatory safety check inside a declared abstraction | Search all reachable states for conflicting certificates, split finality and certificate-free finalization | Complete enumeration of the encoded finite state space; no sampling interval | No run-time deviation recorded; abstraction exclusions are explicit | Bounded analytic/model evidence only |
| Cross-border prototype | Laboratory verification and falsification | 5-of-7 two-phase certificate; 84 unequal-currency transfers; restart, duplicate, stale-policy, amount-mismatch and two-key equivocation scenarios | Latency quantiles plus binary safety/rejection outcomes | No run-time deviation recorded; no preregistration or external replication | Internal prototype evidence |
| Learned privacy attacks | Synthetic red-team benchmark | Compare rotation-only, relay-standardized and shielded/batched profiles for network and compromised-PIP attackers | Two seeds; unseen-user and independent-generator splits; AUC and ranking summaries | No preregistration; results are diagnostic and must not be called confirmatory population privacy evidence | Synthetic benchmark evidence |
| Differential privacy | Mechanism/property validation | Person-level add/remove adjacency; contribution bound three; twelve-release accountant | 10,000 neighbour checks; utility across candidate annual epsilon totals | No run-time deviation recorded; selected epsilon remains an example, not a policy recommendation | Mechanism test and simulated utility only |
| AML/CFT graph benchmark | Primary synthetic comparison plus exploratory heterogeneity | Network-view PR-AUC minus PIP-local PR-AUC across 16 independent graphs and four generator families | Paired bootstrap interval, Wilcoxon and sign test; family effects shown separately | No preregistration; Wilcoxon/sign results do not override heterogeneous family evidence | Predictive synthetic evidence, not FATF effectiveness |
| Sanctions screening | Calibrated held-out benchmark | Threshold selected on calibration data; held-out entity-disjoint test; prevalence-adjusted workload | PR-AUC, ROC-AUC, Brier score, ECE, recall/FPR and scenario workload | No operational customer distribution or independent multilingual adjudication | Official-list snapshot plus generated-query benchmark |
| Economic limits | Analytical identification and decision support | Feasible holding/flow/remuneration set under explicit exposure and policy constraints | Identified ranges and sensitivity, not a point estimate of causal welfare | No jurisdictional microdata; no causal demand or run-risk estimate | Illustrative/analytical policy method |
| Performance | Scenario falsification and qualification design | Seven open-loop tandem-queue scenarios, including a 40k TPS plus region-loss overload control | p50/p95/p99 latency, observed arrivals and SLO pass/fail | Service demands are declared inputs, not hardware measurements | Queueing-simulation evidence; national scale not demonstrated |

## Multiplicity and interpretation rule

The package spans several evidence families but does not combine their p-values into a global success claim. Statistical tests are interpreted only within their declared family. A positive result in one domain cannot compensate for a failed or missing gate in another. The 40k overload-control failure, privacy residual leakage, heterogeneous AML family effects and absence of a universal economic optimum are retained as decision-bearing negative or limiting evidence.

## Deviation ledger

No public preregistration existed before these analyses. Consequently, this document does not claim `zero preregistered deviations`; it records that no run-time departure from the checked-in v8 scripts was observed during the verified build. The checked-in scripts, lockfile, generated result files, provenance record and `SHA256SUMS` define the reproducible executed analysis. Any later change to estimands, thresholds, exclusions, generators, seeds, scenario inputs or claim language requires a new version, regenerated provenance/checksums and re-review of the affected claim.

## Required wording boundary

- Use “bounded model,” “synthetic benchmark,” “laboratory prototype,” “official-list snapshot,” “analytical method,” or “queueing simulation” as applicable.
- Do not use “field validated,” “production ready,” “national scale demonstrated,” “operational AML effectiveness,” or “universal optimal holding limit.”
- Treat physical multi-region testing, governed real-data evaluation and controlled field evidence as future evidence gates rather than implied completed work.
