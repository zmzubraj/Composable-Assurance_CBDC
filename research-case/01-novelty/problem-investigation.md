# Problem investigation

**Cutoff:** 2026-08-29  
**Claim under investigation:** whether a materially distinct research contribution remains after accounting for the strongest work on composable CBDC implementation, cross-ledger settlement, privacy/compliance design, policy limits and operational qualification.

## Causal bottleneck

CBDC assurance is compositional: a design decision that improves one property can weaken another, while evidence generated for an isolated component does not automatically support a system-level or deployment claim. Existing work supplies strong architecture, interoperability, privacy/AML, policy and resilience components. The unresolved research problem is therefore not the absence of components; it is whether there is a reproducible method that binds heterogeneous claims to explicit evidence maturity, negative controls, failure envelopes and progression gates without allowing one domain's result to compensate for another domain's missing evidence.

## Defeating observations found

- Bharathan and Pillai (2022) already use “composable” for a standards-based CBDC implementation and report working software demonstrations. Any claim to be the first composable CBDC implementation is defeated.
- WO2025085074A1 claims architecture-agnostic cross-system CBDC interoperability with reservation, messages, checkpoints and finalization. Any claim to be the first architecture-agnostic checkpoint/finalization scheme is defeated or, at minimum, legally and technically unsafe to assert.
- Lee et al. (2021), CBDC-AquaSphere (2023), Project Icebreaker, Project Mandala and Project Agorá cover important atomicity, independent-ledger, compliance and real-value settlement surfaces.
- Pocher and Veneris (2022) and Michalopoulos et al. (2025) cover privacy/AML regulation- or compliance-by-design.
- Bernardo et al. (2025) explicitly advocate formal methods for CBDC operational resilience.
- Jin and Xia's peer-reviewed CEV framework (2022) already recommends CBDC technical solutions and verifies them through empirical experiments and formal proof. It is the closest method-level predecessor found so far and defeats any broad claim to be the first CBDC evaluation or verification framework.
- SSRN `5394110` is titled as a cross-border CBDC settlement prototype combining programmable compliance, ISO 20022 and FATF Travel Rule automation. Its title-level overlap is high, but public full-text retrieval was blocked; it remains a decision-blocking unresolved predecessor rather than evidence of either novelty or defeat.

## Surviving bounded question

The potentially differentiating question is whether the manuscript's *joint claim-to-evidence qualification method*—spanning settlement safety, residual privacy leakage and differential privacy, AML/sanctions evidence, adaptive policy limits and staged scale falsification—changes assurance decisions by imposing explicit evidence ceilings and non-compensating gates. A hash-bound feature-level review of the CEV full text now confirms a decision-rule difference between CEV's compensating trade-off logic and C001's proposed non-compensating evidence ceilings, but that difference has not been independently verified as materially novel. The claim remains `UNRESOLVED` pending retrieval or a justified access-limit disposition for the high-risk title-only SSRN predecessor, full-text review of the 11 retained CEV forward citations, further patent/standards coverage, an independent search challenge and submission-time refresh.
