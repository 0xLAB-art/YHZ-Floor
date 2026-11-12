# ACTS-Attack Contract-Sound Stage 0/1 + Agent Pilot Audit Report

**Date:** 2026-10-18  
**Protocol commit:** `4743d186bb64b07f5f81d5448bce3f2ab0237563`  
**Pilot output:** `sp2027/analysis/contract_sound_agent_pilot_20261018/`  
**Deterministic output:** `sp2027/analysis/contract_sound_stage01_hardened_v2_20261018/`

## Executive decision

**NO-GO for scientific interpretation of the 72-session agent pilot.**

The frozen scheduler created all 72 planned session records, but every provider request failed with HTTP 401 before model output, candidate code, certificate construction, target execution, reference adjudication, or blind validation. Consequently:

- the pilot has **zero agent outcomes**;
- C1/C2 paired success rates and discordances are **NOT AVAILABLE**, not zero;
- no representation-sensitivity claim can be made;
- no novelty claim can be promoted from this campaign;
- the failed campaign is retained exactly and must not be repaired by retries or seed replacement.

The deterministic Stage 0/1 infrastructure remains a passed implementation milestone. It does not compensate for the invalid agent arm.

## 1. Tests and observations

### 1.1 Frozen pilot completeness

| Check | Result |
|---|---:|
| Planned sessions | 72 |
| Schedule rows | 72 |
| Session directories | 72 |
| Session manifests | 72 |
| Session result files | 72 |
| Unique ordinals | 1--72 |
| Automatic retries | 0 / declared `no_retries=true` |
| Seed replacement | disabled in freeze |
| Study expansion | disabled in freeze |
| Provider route | `claude-sonnet-4-6-free` |
| Pilot estimated cost | USD 0.00 |
| Certificates | 0 |
| Provider metadata files | 0 |
| Raw model response files | 0 |

### 1.2 Failure taxonomy

All 72 rows are identical at the provider boundary:

- `status=PROVIDER_FAILURE`: 72/72
- `category=HTTP_ERROR`: 72/72
- `error=HTTP 401`: 72/72
- C1: 24 failures
- C2: 24 failures
- C0: 24 failures
- ECDSA: 36 failures
- ChaCha20: 36 failures

A separate metadata-only `/v1/models` request using the configured credential also returned HTTP 401. This distinguishes a current provider/credential rejection from a cryptographic, parser, executor, reference-verifier, or blind-validator failure. No model call was issued by the audit itself.

The provider credential file was present with mode `0600`; its value was not disclosed. Presence of a local key is not evidence that the provider currently accepts it.

## 2. Independent-verification status

Because the provider failed before model output, the following pilot-level stages were not reached:

| Stage | Status |
|---|---|
| Agent-authored artifact | Not run |
| Restricted executor | Not run |
| Target cryptographic predicate | Not run |
| Independent reference verifier | Not run for agent sessions |
| Blind validator | Not run for agent sessions |
| Certificate schema validation | No pilot certificates existed |
| Target-effect evidence | Not established |
| Attributable exploit completion | Not established |
| C1/C2 paired analysis | NOT_RUN |
| C0 agent sanity analysis | NOT_RUN |

Provider failure is a predeclared infrastructure-invalid category. It is retained and reported separately; it is not silently treated as agent failure or success.

## 3. Deterministic Stage 0/1 result retained

The hardened deterministic report remains authoritative for the non-agent controls:

- independent Stage 0 instances: 24/24;
- ECDSA C1/C2 full-interface equivalence: 12/12;
- ChaCha20 C1/C2 full-interface equivalence: 12/12;
- C0 ambiguity counterexamples: 24/24;
- clean valid controls: 10/10 accepted;
- clean invalid controls: 10/10 rejected;
- development defects: 20/20 rejected;
- held-out variants: 20/20 rejected;
- independent reference versus blind-validator disagreements: 0/60;
- deliberately mislabeled fixture disagreements: 2/2 detected;
- public forbidden-field cases: 0/60;
- protected manuscript/result-lock changes: 0.

These results establish deterministic infrastructure behavior under the declared fixture families. They do **not** establish AI-agent representation sensitivity, agent exploit capability, or open-world fault generalization.

## 4. Frozen statistical analysis

The preregistered analysis requires paired C1/C2 primary outcomes over 24 paired instances, exact discordance directions, task-stratified estimates, and a 95% paired bootstrap interval. The promotion criterion requires an absolute effect of at least 0.25 and a bootstrap lower endpoint above zero in the observed direction.

No paired primary outcomes exist because all provider requests failed. Therefore the following are explicitly **NOT_RUN**:

- C1 success rate;
- C2 success rate;
- C1-success/C2-failure discordance;
- C1-failure/C2-success discordance;
- McNemar descriptive test;
- paired bootstrap interval;
- task-stratified effect;
- minimum-effect comparison.

The previous deterministic statistical self-test is implementation validation only and must not be substituted for agent data.

## 5. Trust and artifact gates

The audit confirms that the failed campaign retained:

- one manifest and one result record per scheduled ordinal;
- frozen route and condition metadata;
- no retry or seed replacement evidence;
- no candidate or certificate artifact masquerading as a successful run;
- no changes to the protected manuscript or result-lock inputs.

The pilot freeze file still says `RUNNING_EXACT_FROZEN_PILOT`; this is a bookkeeping defect in the runner's terminal-state recording. It does not alter the raw result: `pilot_results.json` contains all 72 terminal provider failures. The audit report records this inconsistency rather than rewriting the raw freeze file.

## 6. Protected-file verification

Current SHA-256 values remain unchanged:

- `sp2027/analysis/RESULTS_LOCK.json` — `4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39`
- `sp2027/analysis/RESULTS_LOCK_H1PC.json` — `8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103`
- `sp2027/paper/main.tex` — `51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461`
- `sp2027/paper/main.pdf` — `fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a`

No manuscript, existing result, historical denominator, or evidence lock was modified.

## 7. Gate disposition

| Gate | Disposition |
|---|---|
| Commit/protocol freeze | PASS for recorded campaign |
| Exact 72-row schedule | PASS |
| No retries/seed replacement | PASS |
| Provider availability/authentication | **FAIL: 72 HTTP 401 responses** |
| Deterministic sufficiency controls | PASS, prior hardened report |
| Independent deterministic reference adjudication | PASS, prior hardened report |
| Blind validator controls | PASS, prior hardened report |
| Pilot certificate integrity | NOT REACHED |
| Agent target-specific reproduction | NOT REACHED |
| Paired C1/C2 statistical gate | NOT REACHED |
| Novelty/representation-sensitivity claim | **NOT ESTABLISHED** |
| Manuscript immutability | PASS |

## 8. Required next action

Do not rerun this campaign automatically. Before any new agent execution:

1. obtain or explicitly authorize a repaired provider credential/route;
2. perform a metadata-only authentication check and retain its result;
3. repair the pilot terminal-state bookkeeping so a completed provider-failure campaign is marked terminal without changing raw rows;
4. create a new versioned campaign directory and freeze manifest only after the route is accepted;
5. obtain explicit approval for a new provider-backed run; no old seed/session may be silently replaced;
6. rerun the full preregistered 72-session design only if the user accepts the new campaign as a versioned replication.

The current campaign cannot support a scientific GO decision for the agent pilot. The correct disposition is **NO-GO / provider-blocked**, not “null effect.”

## Evidence files

- `PILOT_AUDIT.json`
- `pilot_results.json`
- `schedule.json`
- `EXECUTION_FREEZE.json`
- `STAGE01_HARDENED_REPORT.md`
- `STAGE01_HARDENED_DATA_FLOW.md`
- `/mnt/nvme5/ACTS-Attack/sp2027/analysis/audit_contract_sound_agent_pilot.py`