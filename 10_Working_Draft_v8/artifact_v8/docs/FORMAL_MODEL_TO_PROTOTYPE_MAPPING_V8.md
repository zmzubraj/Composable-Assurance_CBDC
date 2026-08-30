# Formal-model to prototype mapping — v8

**Date:** 2026-08-29  
**Purpose:** Trace the cross-border safety claims from the bounded state model to prototype code, tests, machine-readable results and manuscript language.

## Interpretation boundary

This is a claim-to-code traceability map, not a mechanically proved refinement relation. The abstract model and prototype share the decision vocabulary and checked safety conditions, but the prototype is not generated from the model and no theorem proves that every implementation execution refines a model transition. Model evidence is therefore reported only for the declared abstraction; prototype evidence is reported only for the executed laboratory scenarios.

| Claim / property | Abstract-model representation | Prototype realization | Executable or result evidence | Supported interpretation | Unmodelled / residual gap |
|---|---|---|---|---|---|
| One terminal decision per transaction | Honest per-node decision locks; separate PREPARE and terminal-vote sets | `DecisionNode.dispatch` persists a transaction decision before signing; conflicting requests are rejected | `results/cross_border_model_v5.json`: zero conflicting-certificate violations; `results/cross_border_bft_v5.json`: conflicting ABORT quorum not obtained | Safety survives the explored abstract state space and the two-key laboratory equivocation scenario | No dynamic membership, key recovery, side-channel or arbitrary implementation-refinement proof |
| Quorum intersection under 5-of-7 with at most two equivocating keys | `N=7`, `Q=5`, `F=2`; certificates require quorum votes | `DecisionClient.decide` collects PREPARE and COMMIT quorums; certificate verification checks signer uniqueness and signatures | Model reports 2,013 reachable states and 19,480 transitions with no conflicting certificate; prototype records only two conflicting votes after COMMIT | Bounded certificate safety for the declared signing-key fault model | Not a complete general-purpose BFT liveness or state-machine-replication result |
| No ledger COMMIT or ABORT without a valid certificate | Ledger finalization actions are enabled only by the matching model certificate | `Ledger.verify_decision_certificate` and `Ledger.dispatch(op="finalize")` reject invalid, mismatched or conflicting decisions | Model reports zero commit-without-certificate and abort-without-certificate violations; prototype completed 84 transfers | Certificate-gated finalization is implemented and exercised locally | Does not establish legal finality or production key custody |
| No split finality across the two sovereign ledgers | Unsafe predicate flags `{COMMITTED, ABORTED}` across ledger states | Both ledgers verify the same proposal digest and terminal certificate before finalization | Model reports zero split-finality violations; prototype reports `split_finality_observed: 0` | No split finality was found in the bounded model or executed prototype scenarios | Network partitions of arbitrary duration and all operational recovery sequences are not exhausted in the prototype |
| Evidence atomicity | Model decision is bound to one decision value; evidence details are outside the abstraction | `DecisionNode.verify_evidence` checks transaction, digest, currency, amount, signed PI/Q/CA/CB/PA/PB and expiry | Prototype rejects a mismatched quote and stale compliance authorization | The laboratory decision certificate is bound to the tested payment, FX, compliance and prepare evidence | Semantic correctness of external policy/list content is assumed, not proven |
| Idempotent recovery | Repeated delivery is abstracted as no new unsafe transition | SQLite-backed ledger/decision state persists across restart; repeated finalization returns idempotently | `restart_delivery_succeeded: true`; `duplicate_finalization_idempotent: true`; restart timing recorded | The exercised single-host crash/restart and duplicate-delivery path is recoverable and idempotent | No certified storage, multi-region disaster recovery, RTO/RPO qualification or corruption testing |
| Monetary conservation on each domestic ledger | Monetary balances are outside the cross-border decision abstraction | `Ledger.invariant` checks issued supply against holdings plus escrow and reserve/liability composition | Both ledger invariants report `supply_ok: true` and `liability_composition_ok: true` after the run | The executed transfers preserve the coded domestic accounting invariants | The state model does not prove these monetary equations; external reserve systems are simulated |
| Cryptographic binding and tamper rejection | Signature unforgeability is an explicit model assumption | Canonical JSON, SHA-256 digests and Ed25519 signatures bind prototype evidence and votes | `tests/test_cross_border_crypto.py` checks serialization order independence, tamper rejection and malformed-signature rejection | The selected library operations and canonicalization wrapper pass the included unit tests | Not certified cryptographic implementation, HSM use, side-channel review or formal cryptographic proof |

## Evidence chain

1. `scripts/cross_border_model_v5.py` produces the bounded state-space result.
2. `scripts/cross_border_bft_v5.py` produces the laboratory-prototype result.
3. `tests/test_cross_border_crypto.py` checks canonicalization and signature rejection behavior.
4. `scripts/verify_v8.py` fail-closes on the central state counts, prototype outcomes and monetary invariants.
5. `RUN_ALL.sh` executes tests before regenerating results, figures, manuscripts, provenance and checksums.

The manuscript must not describe this mapping as formal refinement, production certification, independent replication or national deployment evidence.
