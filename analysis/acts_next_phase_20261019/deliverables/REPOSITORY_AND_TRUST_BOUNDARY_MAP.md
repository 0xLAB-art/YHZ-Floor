# Repository and Trust-Boundary Map — ACTS-Attack

**Phase:** `acts_next_phase_20261019` (additive; no historical file modified)
**Date:** 2026-10-20
**Primary sources:** `stage0/AGENT1_TRUST_BOUNDARY_MAP.md` (641 lines, independently re-derived),
`stage3_boundary/STAGE3_BOUNDARY_ANALYSIS.md` (854 lines, 14 candidate ingresses),
`stage1_attribution/s1_protocol.md` §2 (the 15-object evidence chain).

Every file:line reference below was checked against the working tree in this
session. Where a fact is asserted by a prior report but not re-derived here, it
is marked **[re-derived]** or **[asserted]**.

---

## 1. The live campaign path (authoritative)

```
run_contract_sound_agent_replacement_v1.py          <- driver
  └─ provider_adapter.ClaudeProvider                 <- ONLY outbound network call
  └─ contract_sound_repaired_pipeline.py:102-148      <- bwrap sandbox + execution
       ├─ bwrap setup          :79-99   (fail-closed, --unshare-net, --ro-bind / /)
       ├─ subprocess            :117-127 (candidate execution)
       ├─ stdout/stderr capture :136-137
       └─ candidate_output.json  :147    (written by the harness from the capture)
  └─ run_contract_sound_agent_pilot_free_v2.py:86-100  <- certificate construction
  └─ contract_sound_stage01_reference_verifier_v2.py:117-133  <- adjudicator (bundle on argv)
  └─ contract_sound_stage01_validator_v2.py:39-87             <- blind validator (cert on stdin)
  └─ audit_contract_sound_replacement_pilot.py:18,:90-102     <- final claim aggregation
```

`run_contract_sound_agent_replacement_v1.py` is the path that produced the
72/72 SUCCESS campaign recorded in
`contract_sound_agent_replacement_20261018/`. The two earlier campaigns are
infrastructure-invalid (72/72 HTTP 401; 72/72 `HARNESS_FAILURE`).

### 1.1 Object-by-object trust map of the live path

| # | Object | Produced by | Bound to the next link? | Evidence |
|---|---|---|---|---|
| 1 | Model / scripted producer identity | provider adapter | **No** — `claims.immutable_hosted_model_identity` is set to `NOT_ESTABLISHED_BY_THIS_CERTIFICATE` | `free_v2:98-100` |
| 2 | Program source bytes + SHA-256 | producer | **Partially** — the certificate carries `agent_artifact{path,sha256}` = the program source | `free_v2:86-100` |
| 3 | Executed program bytes | bwrap sandbox | **No** — nothing records the bytes that were actually executed | `repaired_pipeline:117-127` |
| 4 | Invocation command + argv | harness | **No** — not recorded in any evidence file | — |
| 5 | Execution environment identity | harness | **No** — `environment_hash` is the digest of the constant `boundary.json` label file, not of an environment | `free_v2:86-100` |
| 6 | Input / public-instance digest | harness | **No** — no input digest is recorded | — |
| 7 | Target identity + target-state digest | harness | **No** — `base_instance_id` is a string label | `free_v2:86-100` |
| 8 | Attempt / session identity | harness | **Weak** — `session_id` is present and the validator checks `trace.session_id == execution.session_id` | `validator_v2:67-69` |
| 9 | Captured stdout / stderr | harness | **No** — captured at `repaired_pipeline:136-137` but never hashed into the certificate | — |
| 10 | Parsed `candidate_output.json` + digest | harness | **No** — the certificate never names it | — |
| 11 | Trusted execution-observer record | — | **DOES NOT EXIST** in the live path | — |
| 12 | Independent cryptographic reference result | reference verifier | **Yes** — the verifier reads the target state and the candidate itself | `reference_verifier_v2:117-133` |
| 13 | Signed evidence records | — | **DOES NOT EXIST** — the certificate schema is `additionalProperties:false` and carries no signature field at all | `contract_sound_artifact_schema_v1.json:130` |
| 14 | Aggregated certificate | harness | internal consistency only | `free_v2:86-100` |
| 15 | Final attributed-success claim | aggregation | **Producer-declared** — `claims.attribution = "PROVEN"` is set from *execution status alone*, before any verifier verdict, and the validators then *require* that self-declared value | `free_v2:98`; `replacement_v1:168-170`; `validator_v2:83-84` |

**Which component is trusted to observe execution?** In the live path: **none**.
The only party that sees the program's stdout is the harness that produced it,
and the harness also writes the certificate that claims the program was
executed. The three "hashes" in `execution{executor_hash,parser_hash,environment_hash}`
are digests of the harness's own constant label files — the "constant label
digests" observation in `AGENT1_TRUST_BOUNDARY_MAP.md`.

## 2. The two findings the prior research did not foreground

1. **The attribution claim is producer-declared, not verifier-derived.**
   `claims.attribution = "PROVEN"` is computed from the *execution status*
   (`EXECUTED` and condition in {C1,C2}) and written into the certificate
   before the reference verifier or the blind validator has run. Both
   validators then *require* `claims.attribution == "PROVEN"`
   (`validator_v2:83-84`), so the claim is validated against itself.

2. **The blind validator is a consistency checker, not a truth gate.**
   `AGENT_PILOT_RESULTS_SUMMARY.json` shows it **ACCEPTED 24/24
   cryptographically-false C0 controls**. Only the reference verifier
   distinguishes a true result from a false one. Any claim that the *validator*
   endorses a solution is therefore meaningless on its own.

## 3. Ingress / egress survey (re-derived, 14 candidates)

| Direction | Result |
|---|---|
| HTTP servers, socket listeners, Flask/FastAPI/http.server under `sp2027/analysis/` | **0** |
| `argparse` / `sys.argv` / stdin in the five campaign runners | **0 / 0 / 0** (each) |
| Outbound network | provider adapter only (`https://api.apmix.ai`) |
| Certificates accepted from outside the process | **none** — the certificate is constructed in-process, in the same loop iteration, immediately after execution (`replacement_v1:165 → :172 → :175 → :176`) |

**Finding token:** `NO_EXTERNAL_CERTIFICATE_COMPOSITION_INTERFACE_FOUND_IN_INSPECTED_REPOSITORY_PATHS`

This is **source-level negative evidence over the inspected paths**, not a proof
of universal impossibility. Stage 3 (`STAGE3_BOUNDARY_ANALYSIS.md`) applied the
six-point qualifying test to 14 candidate ingresses: **0/14 pass K1
(identifiable owner and authorisation)**.

**Finding token:** `NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED`

> The decisive near-miss is `acts_next_phase_20261019_v2/stage3_boundary/ingress_gateway.py`
> in the concurrent sibling tree. Its own docstring says *"This gateway supplies
> the missing boundary"* — it was created on 2026-10-20 as a research artefact.
> It satisfies criteria K2–K6 and fails K1 by construction. It is recorded here
> so that no reader mistakes it for a pre-existing ingress.

## 4. Structural reason the demonstrated gap is not live-reachable

The Stage 1 cases C02 (`credited_program_not_executed`) and C03
(`submitted_output_not_observed`) substitute, respectively, the program source
and the runtime output **after** the trusted observer has signed its record.
In the live path the certificate is assembled in-process from the very artefacts
the harness just produced, so those two artefacts are not *separable* at the
point where the certificate is built. A component-level **capability** gap is
therefore demonstrated (the frozen Stage01 pair accepts both), while deployed
**reachability** is not.

## 5. The Stage 1 trust boundary (this phase's new construction)

`stage1_attribution/` introduces the missing trusted party:

```
   producer (untrusted)            trusted execution observer        independent reference verifier
   ────────────────────            ─────────────────────────        ─────────────────────────────
   candidate.py  ──▶  (untrusted, never holds an observer key)
                             │  executes the program itself
                             │  hashes program bytes (before AND after exec)
                             │  captures stdout/stderr
                             │  derives candidate_output.json from ITS OWN capture
                             │  signs an execution_observation record
                             ▼
                      signed observation  ──┐
                                            ├──▶  bundle.json  ──▶  attribution evaluator
   signs an artifact_record ────────────────┘                        (tri-state)
                             │                                           ▲
                             │  stdout (pinned by the observer's digest) │
                             ▼                                           │
                       reference verifier ─── signed reference_verdict ───┘
                             │  holds the PRIVATE target state
                             │  uses the FROZEN ecdsa_valid / chacha_valid
                             ▼
                       ATTRIBUTED_SUCCESS | REJECT | INCONCLUSIVE
```

| Trust property | How it is obtained |
|---|---|
| The observer's key is not derivable from public data | fresh `Ed25519PrivateKey.generate()` at setup; private material kept in a 0600 keystore **outside** the repository (fuseblk reports 0777 and ignores `chmod` — deviation D-05) |
| The producer cannot substitute the runtime output | the observer writes `candidate_output.json` from its own stdout capture, and signs the stdout digest; the evaluator re-derives the output artifact from the captured stdout |
| The reference verdict cannot be transplanted | the verdict is bound to `stdout_sha256` + `target_state_sha256`; the evaluator joins it to the bundle's stdout and to the harness-side expectation |
| Freshness / anti-replay | six-field signed context (`kind, domain, target_id, attempt_id, epoch, role`) + `context_validator.ReplayState`; the unmodified `heb1_remediation_v1/context/context_validator.py` enforces it |
| Role authorisation | `protected_signing.IssuerPolicy` maps each role to exactly one evidence kind; the expected role is derived from the *kind*, not from the record's self-declared role |
| The measurement itself is frozen | `heb1_remediation_v1/integrity/manifest_verifier.py` (unmodified) preflights 77 files before the run and is re-verified after it |

## 6. Files read but not modified (integrity anchors)

| File | SHA-256 | Role |
|---|---|---|
| `sp2027/analysis/contract_sound_stage01_validator_v2.py` | `f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a` | frozen blind validator, used as the Stage 1 baseline |
| `sp2027/analysis/contract_sound_stage01_reference_verifier_v2.py` | `15bb4095ee39f6ff558c5989450238e20f1d371712b31817d657f49232c7584b` | frozen cryptographic predicate, imported by the Stage 1 reference verifier |
| `sp2027/analysis/run_contract_sound_stage01.py` | — | frozen fixture generator, imported for target instances |
| `sp2027/analysis/heb1_remediation_v1/signing/protected_signing.py` | — | unmodified, imported by path |
| `sp2027/analysis/heb1_remediation_v1/context/context_validator.py` | — | unmodified, imported by path |
| `sp2027/analysis/heb1_remediation_v1/integrity/manifest_verifier.py` | — | unmodified, imported by path |

Both Stage 1 digest pins were recomputed in this session. The Stage01 wrapper's
`FROZEN_VALIDATOR_SHA256` constant is **correct** — it pins the *validator*
file, and the Stage 1 reference-verifier pin is a separate, new value.

## 7. Trust assumptions that are *not* satisfied in the live path, and cannot be fixed without an authorised ingress

1. No signed evidence at all in the live certificate format.
2. No record of the executed bytes, argv, environment, stdout digest, or input digest.
3. No target-state digest binding.
4. No attempt/epoch binding that a third party could check.
5. No tri-state: absence of evidence is indistinguishable from evidence of failure in the frozen validator.
6. The certificate is assembled by the same process that produced the artefacts it certifies.

Items 1–5 are **fixable inside the evaluation harness** without any change to
the trust model. Item 6 is the structural blocker for a *live* false
attribution and is the reason Stage 3 returns
`NO_AUTHORIZED_REACHABLE_INGRESS_IDENTIFIED`.
