# IAR-A — Cross-Boundary Composition Against the Real Stage01 Pipeline

Date: 2026-10-19 (independent adversarial replication, stage A)
Status: executed; single deterministic run; campaign artifacts read-only; protected locks verified unchanged.

## Method

Read-only invocation of the frozen stage01 components on **new inputs** (no campaign
artifact was modified):

| component | path | sha256 |
|---|---|---|
| blind validator v2 | `sp2027/analysis/contract_sound_stage01_validator_v2.py` | `f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a` |
| reference verifier v2 | `sp2027/analysis/contract_sound_stage01_reference_verifier_v2.py` | `15bb4095ee39f6ff558c5989450238e20f1d371712b31817d657f49232c7584b` |
| base case | `contract_sound_stage01_hardened_v2_20261018/stage1/clean/clean_01` | public cert `f724138fb6bc3a590c274c743f35c466b86014e39b9210263d72f592aee102bf`; candidate `e1647eab901a58ebef676f731590014cc86620bb21cf5a594bebab2e65a3aae7` |
| generator | `heb1_crossboundary_20261019/iar/iar_a_stage01_transfer.py` | `27c01caba5a1fbf8e56e484ebad22a1277e05ba6e2c100b2889eb1507448c01b` |
| results | `heb1_crossboundary_20261019/iar/iar_a_20261019/iar_a_results.json` | `c3f225825d8b0989d6a14336ba44e80342c572a23bee9b64b79448f300401313` |

Ground truth is an explicit two-run registry written next to the results and never
supplied to either component:

- **X** — session `iar-session-X`, candidate `x_candidate.json` (`d` copied, `k=00*32`),
  effect `NOT_OBSERVED`, executor `iar-executor-X`.
- **Y** — session `stage01-hardened-session-001`, candidate `e1647eab...` (valid),
  effect `OBSERVED`, executor `stage01-executor-v1`.

The certificates are new assemblies of per-run records in the real stage01 schema. No
field was altered after assembly except in the variants labelled as rewrites.

## Results

| variant | composition | blind validator | reference verifier |
|---|---|---|---|
| A0 baseline | `clean_01` unmodified | `ACCEPT` (`public-evidence-consistent`) | `ACCEPTED` (crypto true, cert errors `[]`) |
| A1 selection-only splice | execution/trace/authorship from **X**, candidate/effect from **Y** | `ACCEPT` | `ACCEPTED` |
| A1b session-binding control | execution claimed **Y**, trace from **X** | `REJECT` (`execution-session-binding`) | `REJECTED` (`execution-session-binding`) |
| A2 trace-hash wrong | `execution.trace_hash = 00*32` | `ACCEPT` | `ACCEPTED` |
| A2 agent-session mismatch | `agent_artifact.json` session Y, execution X | `ACCEPT` | `ACCEPTED` |
| A2 reference claim unbound | public cert claims `reference_oracle_acceptance = ACCEPTED` | `ACCEPT` | `ACCEPTED` |
| A3 relabeled trace | X trace bytes, `session_id` rewritten to Y | `ACCEPT` | `ACCEPTED` |

A1 certificate: `1e738566ae78a61806c55ca6b54add650da3defce9543c3e706506f5b2e0b0f2`.
A3 certificate: `7f7b3fdcf7b997ed550c4e9e55a25a21e57682b41160ee6aaa4c081d382ad0cf`.
In A1 the submitted candidate (`e1647eab...`) does not match the registry's candidate
for X (`aed7e1d8...`), and the registry effect for X is `NOT_OBSERVED`.

## Interpretation

- The real pipeline already enforces execution-session and task-session binding:
  A1b is rejected by both components. The naive HEB-1 B5 split (trace X, execution Y)
  does not transfer unmodified.
- The pipeline does **not** bind the execution trace or the authorship record to the
  candidate hash. A selection-only composer (capability C0: pick records from genuine
  runs, no byte alteration) can pair a failed run's trace/authorship with a successful
  run's candidate; both real components accept (A1). Verdict-level effect demonstrated:
  the blind validator emits `ACCEPT` for a certificate that is false under the
  two-run registry.
- The reference verifier's `ACCEPTED` certifies that the submitted candidate is valid
  and the certificate is internally consistent, not that X executed the submitted
  candidate. The false attribution is carried by the certificate's
  `execution_identity`/`attribution` claims.
- Declared-but-unchecked fields (`execution.trace_hash`), the unbound authorship
  session, and the unbound `reference_oracle_acceptance` claim are all accepted (A2).
- Unsigned metadata can be relabeled (A3); this pipeline has no signatures or trusted
  anchors, so authenticity is out of scope for its checks.

## Limits and threat model

- The splice requires the certificate/evidence **composer** to be able to select
  records across runs (or to rewrite unsigned metadata). If the composer is trusted
  harness code, A1 is not reachable; the result is an aggregator/provenance boundary,
  not a break of a trusted production pipeline.
- Per-run records are synthetic (as in the stage01 deterministic fixtures); only the
  acceptance logic of the real components is exercised, unchanged.
- The missing binding (evidence ↔ artifact/material) is the documented RATS /
  in-toto principle. IAR-A is a real-pipeline instance and impact measurement, **not**
  a new binding mechanism. Novelty remains **not established**; impact evidence is
  strengthened.
- Single deterministic run; components frozen; no campaign artifacts modified;
  protected locks verified unchanged.

## Next

- **IAR-B** — authenticated-provenance baseline (`V3-sig` / `V3-full`, offline Ed25519):
  determine whether signing/anchoring subsumes the A1 splice, and run the B5'
  metadata-rewriting variant under the same registry.
- **IAR-C** — independent generation (structurally independent of V2) with honest
  success/failure bundles and claims at levels 1–6; measure supported-level vs
  requested-level (partial-claim acceptance).
