# Repository and Trust Boundary Map

**Project:** ACTS-Attack  
**Stage:** Stage 1 — End-to-End Attribution  
**Working directory:** `sp2027/analysis/acts_next_phase_20261019_v2/`  
**Date:** 2026-10-20  
**Status:** COMPLETE

---

## 1. Dataflow Map (Source Locations)

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PREPARATION (e2a.prepare)                      │
│  e2a/prepare.py  →  provision_trust()                               │
│    ├─ protected_signing.generate_issuer() ×3 (Ed25519, fresh random)│
│    │    → keys/ (on tmpfs if fuseblk, else STAGE1_ROOT/keys)       │
│    ├─ write_public_bundle() → frozen/issuers_public.json            │
│    ├─ write_frozen_artifacts() → frozen/{cases,labels,trust,..}    │
│    └─ write_manifest() → E2A_FREEZE.json (schema /1)               │
│        Preflight: manifest_verifier.verify_manifest() — fail-closed │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     EXECUTION (e2a.runner)                          │
│  e2a/runner.py  →  execute_run()                                    │
│    for each case (22):                                              │
│      ├─ build_instance() → public instance JSON                     │
│      ├─ producers.produce_source() → program source text            │
│      ├─ observer subprocess (e2a/observer.py):                      │
│      │   ├─ execute_observed(): memfd exec of source               │
│      │   ├─ captures stdout/stderr/returncode                      │
│      │   ├─ parse_candidate_output() → candidate_output.json       │
│      │   ├─ sign_record() with OBSERVER key → observation envelope │
│      │   └─ writes observation.json                                │
│      ├─ reference subprocess (e2a/reference.py):                    │
│      │   ├─ recomputes crypto predicate from private target state  │
│      │   ├─ signs with REFERENCE key → reference envelope          │
│      │   └─ writes reference.json                                  │
│      ├─ assemble_e2a_certificate() → certificate.e2a.json           │
│      ├─ aggregator.evaluate() → decision (REJECT/ATTRIBUTED_..)    │
│      ├─ aggregator.sign_claim() → claim.e2a.json (AGGREGATOR key)   │
│      └─ run_baseline() → Stage 01 frozen validator + reference      │
└─────────────────────────────────────────────────────────────────────┘
```

### Component → File Mapping

| Component | File | Responsibility |
|-----------|------|----------------|
| canonical | `e2a/canonical.py` | Constants, serialization, hashing |
| remediation | `e2a/remediation.py` | Signed context, replay ledger, manifest verifier, protected signing loader |
| producers | `e2a/producers.py` | Scripted program source generation |
| observer | `e2a/observer.py` | Trusted execution observer (TEO) — executes + captures + signs |
| reference | `e2a/reference.py` | Independent cryptographic reference adjudicator |
| aggregator | `e2a/aggregator.py` | Final attribution decision (ordered checks 1–9) |
| baseline | `e2a/baseline.py` | Stage 01 certificate builder + frozen validator/reference |
| cases | `e2a/cases.py` | 22 case definitions |
| truth | `e2a/truth.py` | Ground truth labels |
| adjudicate | `e2a/adjudicate.py` | Adjudication logic |
| prepare | `e2a/prepare.py` | Pre-execution trust provisioning + freeze |

### Frozen Audited Components (remediation v1)

| Component | Path | Role |
|-----------|------|------|
| protected_signing | `heb1_remediation_v1/signing/protected_signing.py` | Ed25519 issuer keys, sign/verify records, key permission check (0600) |
| integrity | `heb1_remediation_v1/integrity/manifest_verifier.py` | Fail-closed manifest verification (preflight) |
| context | `heb1_remediation_v1/context/context_validator.py` | Six-field context validation + replay ledger |
| signing | `heb1_remediation_v1/signing/` | Protected signing primitives |
| stage01 | `heb1_remediation_v1/stage01/` | External Stage01 wrapper |

---

## 2. Trust Boundaries

### Boundary A: Producer → Observer (Trusted Execution)
- **Producer** (`producers.produce_source`) is **untrusted** — generates source text.
- **Observer** (`observer.py`) is **trusted** — independently executes source from memfd, captures actual stdout/stderr/returncode, signs the six-field context.
- **Trust boundary:** The evidence chain does **not** rely on producer-supplied hashes alone; the observer re-executes and independently captures output.
- **Limitation:** Observer is local/in-process; path confinement has TOCTOU limitations (documented in remediation v1).

### Boundary B: Observation → Reference (Independent Adjudication)
- **Reference** (`reference.py`) is **trusted** — recomputes the cryptographic predicate from private target state (never reads stored labels), signs with REFERENCE key.
- **Trust boundary:** Reference verdict is independent of the observation; cross-record consistency is checked by the aggregator (candidate digest, stdout pin, target digest, target ID).

### Boundary C: Aggregator (Final Claim)
- **Aggregator** (`aggregator.py`) is **trusted** — makes the final REJECT / ATTRIBUTED_SUCCESS / INCONCLUSIVE decision using 9 ordered checks, then signs the claim with AGGREGATOR key.
- **Missing evidence → INCONCLUSIVE**, never counted as zero failure.

### Boundary D: Baseline (Stage 01 Comparison)
- **Stage 01 validator/reference** (`heb1_remediation_v1/stage01/`) are **frozen external components** used for comparison only; not the primary decision path.

---

## 3. Attack Surfaces Evaluated

| Attack | Vector | Result | Boundary holding |
|--------|--------|--------|------------------|
| Identity swap | Declared artifact ≠ executed program | REJECT | Executed-program-identity check |
| Output swap | Certificate declares output not produced | REJECT | Candidate-output-substitution check |
| Stale attempt | Attempt ID mismatch | INCONCLUSIVE | Observation-context-binding |
| Context conflict | Target/attempt/epoch conflict | INCONCLUSIVE | Observation-context-binding |
| Replay | Replayed observation | REJECT | Observation-replayed check |
| Reference mismatch | Reference doesn't adjudicate this observation | REJECT | Cross-record consistency |
| Missing observation | No observation record | INCONCLUSIVE | Evidence-record-missing |
| Missing reference | No reference record | INCONCLUSIVE | Evidence-record-missing |

---

## 4. Reachable Ingress Assessment

| Question | Finding |
|----------|---------|
| External certificate upload gateway | None identified in inspected paths |
| Webhook / aggregation consumer | None identified |
| Deployed submission gateway | None identified (external Stage01 wrapper is local CLI only) |
| Authorized reachable ingress, pre-Stage 3 | `NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED` |
| Authorized reachable ingress, post-Stage 3 | **Superseded**: a controlled loopback ingress (`stage3_boundary/ingress_gateway.py`) now exists and has been exercised |

**Conclusion (updated after Stage 3):** The local construction/execution boundary was already reachable, but the *evaluation path* had no external interface through which untrusted evidence could arrive. Stage 3 constructed that interface — a loopback HTTP gateway in front of the frozen aggregator — and exercised it with a live local target. Eleven non-positive-control submissions over that ingress produced zero attributions. No **externally** reachable gateway exists in this project, and that remains true; the superseded finding concerns the evaluation path, not the wider project.

---

## 5. Objects Authenticated (per handoff §8)

| # | Object | Authenticated by |
|---|--------|------------------|
| 1 | Producer identity | Signed observation (observer role) |
| 2 | Program source bytes + SHA-256 | Observer hash + signed record |
| 3 | Executed program bytes | Memfd exec (identical to declared) |
| 4 | Invocation command + args | Observation `command` field |
| 5 | Execution environment + versions | Observation `interpreter` + `environment` |
| 6 | Input/public-instance digest | `public_target_digest` |
| 7 | Target identity + state digest | `target_id` + `target_state_sha256` |
| 8 | Attempt/session identity | `attempt_id` |
| 9 | Captured stdout/stderr | Observer capture + signed |
| 10 | Parsed candidate_output.json + digest | Observer parse + `parsed_candidate_sha256` |
| 11 | Trusted observer record | Signed observation envelope |
| 12 | Independent crypto reference | Signed reference envelope |
| 13 | Signed evidence + issuer role | Ed25519 per role (observer/reference/aggregator) |
| 14 | Aggregated certificate | `certificate.e2a.json` |
| 15 | Final attributed claim | `claim.e2a.json` signed by aggregator |

---

## 6. Conclusion

The trust boundary map shows a defensible local attribution chain: untrusted producer → trusted observer (independent execution) → trusted reference (independent recomputation) → trusted aggregator (ordered checks) → signed claim. Stage 3 added the missing network ingress and showed the chain still refuses every altered or fabricated submission. The chain does not rely solely on producer-supplied hashes.