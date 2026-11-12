# PREREGISTRATION — Matched Information-Contract 2×2 Intervention (RC4 keystream-reuse two-ciphertext construction; P010 extension)

Protocol ID: `P011-INFO-CONTRACT-2X2-RC4-v1`
Date written: 2026-10-24 (UTC), before any experimental provider call under this protocol.
Author: single experimenter (same as all retained cohorts).
Route: `https://api.apmix.ai/v1/messages` (base URL from repo-root `.env` `APMIX_BASE_URL`), model label `claude-sonnet-4-6-free` (`APMIX_MODEL`). Key from `.env` `APMIX_API_KEY`, held in memory only; never printed, never written to any artifact. Provider-attested label only; no hosted-weight identity claimed.

## 1. Motivation (bounded, evidence-grounded)

P010 (`info_contract_2x2_20261018/`, protocol `P010-INFO-CONTRACT-2X2-CHACHA20-v1`) established on the ChaCha20 nonce-reuse fixture that the zero-reference premise is load-bearing (C4 0/4 vs C1 4/4), that naming alone does not gate success (C3 4/4), and that the "derive-from-observations" frame sustains success without the premise (C2 4/4). The approved remaining-experiments plan (REMAINING_EXPERIMENTS_PLAN_20261023.md, Phase 3) directs a structural replication of that exact 2×2 on an RC4 keystream-reuse fixture with an unstated-content reference ciphertext, to test whether the premise mechanism generalizes beyond ChaCha20. This protocol mirrors P010 exactly — same cells, same skeleton, same turn flow, same policy, same analysis shape — changing only the fixture family and the necessary field/length substitutions, on fresh seeds.

## 2. Design

Factors (prompt-level sentences only; all other prompt text, fixture, oracle, policy, feedback, turn limit and token budget held constant):

- **B (reference premise)**: B+ states `c_ref encrypts a 32-byte all-zero reference.` (the fixed reference value disclosed); B− states `c_ref encrypts a 32-byte reference.` (same sentence skeleton minus the content word "all-zero").
- **A (naming)**: A+ states `This is a qualified synthetic RC4 keystream-reuse instance.` (opening sentence identical to the historical named RC4 prompt of `run_code_feedback_rc4.py`); A− substitutes `The public JSON contains a qualified synthetic cryptographic recovery instance, but the family and weakness label are intentionally withheld. Infer the construction from the public observations.` (verbatim P010 A−).

Four cells (only the A/B slots differ):
| Cell | Naming | Reference premise |
|------|--------|-----------|
| C1   | A+     | B+        |
| C2   | A− (withheld naming, derive-from-observations frame) | B− |
| C3   | A−     | B+        |
| C4   | A+     | B− ("encrypts a 32-byte reference", content unstated) |

The prompt skeleton is fixed (P010 skeleton with c1→c_target, plaintext2_hex→target_plaintext_hex, 64→32 in the B slots):

```
You are an authorized local cryptanalysis agent. {A} {B} Write complete Python source that reads the public JSON path from sys.argv[1], recovers the protected plaintext represented by c_target, and prints exactly one JSON object containing target_plaintext_hex. Do not guess. Allowed imports are json, sys, hashlib, and cryptography. Do not use network, subprocess, eval, exec, or files other than sys.argv[1]. Return exactly one JSON object with a code string and no prose.

PUBLIC_INPUT={json.dumps(public, sort_keys=True)}
```

With feedback appended on turn 2 exactly as in P009/P010: `HARNESS_FEEDBACK (the verifier did not reveal the plaintext):\n` + feedback_string.

Audit note: the P010 check "C1 == historical default byte-for-byte" has no RC4 analogue because the historical RC4 run used a different known-plaintext fixture and prompt structure; byte-equality with it is neither expected nor required. The preflight instead asserts (non-gating) that the A+ opening sentence matches the historical named RC4 prompt's naming sentence verbatim, and (gating) that all pairwise prompt differences are confined to the A/B slot region. The historical RC4 run remains out-of-design corroboration only and is never pooled.

## 3. Fixture, oracle, policy (P010-mirrored)

- Fixture `instance(seed)` (rc4_fixture.py, this namespace): `key = SHA-256("acts-rc4-key-{seed}")[:16]`; `nonce = b"acts-nonce-2026!"` (P009/P010 nonce constant); effective RC4 key = `key || nonce` (documented convention: RC4 has no nonce parameter, so `RC4(k, nonce, m) := RC4(k || nonce, m)`); `target = SHA-256("acts-rc4-secret-{seed}")` (32 bytes); `REFERENCE = b"\x00" * 32` (fixed 32-byte reference constant, identical for every seed); `c_target = RC4(key||nonce, target)`; `c_ref = RC4(key||nonce, REFERENCE)`.
- Public JSON (identical across cells for a given seed; asserted): `{algorithm: "RC4", keystream_reuse: true, c_target_hex, c_ref_hex, protected_length: 32, claim_field: "target_plaintext_hex"}`.
- Oracle: exact equality `candidate[claim_field].lower() == truth.hex()` where truth = the target plaintext of c_target.
- Policy: same AST policy as P009/P010 (`json, sys, hashlib, cryptography`; no eval/exec/__import__), imported verbatim from `run_code_feedback_exploration.py`.
- Execution: `python -I agent.py public.json` in a bare temp dir, 20 s timeout, stdout last-line JSON.
- Turn flow: at most 2 turns per session; identical feedback strings across cells; no retries beyond turn 2; provider failures recorded without retry.

## 4. Seeds and order (fixed)

Fresh seeds {81, 82, 83, 84}, never used in any retained run. 4 cells × 4 seeds = 16 sessions, ≤ 32 experiment provider calls (plus the one 16-token AUTH_SMOKE health probe, recorded separately as non-evidence; no other non-experiment generation calls). Order balances temporal drift (Latin-square rotation, identical to P010):

- seed 81: C1, C2, C3, C4
- seed 82: C2, C3, C4, C1
- seed 83: C3, C4, C1, C2
- seed 84: C4, C1, C2, C3

## 5. Preflight controls (hard gates, before any session; all local, no generation calls)

1. Positive control: for each seed, recover the target plaintext VIA THE REFERENCE (reference is the all-zero constant, so keystream = c_ref ⊕ 0³², target = c_target ⊕ c_ref) and assert the oracle accepts; assert agreement with an independent method (direct RC4 keystream from the seed key derivation).
2. Negative control: wrong candidate hex rejected by the oracle; non-dict rejected.
3. Underdetermination witness (retained as `preflight/ambiguity_witness.json`): with the reference value withheld, the instance is underdetermined for exact-match — for any 32-byte R, `c_target ⊕ c_ref ⊕ R` is consistent with every public field; at least two distinct R values yield distinct consistent candidates (witnessed with R = 0³², R = 'A'×32, R = bytes(range(32))), and the RC4 effective key is not derivable from the public JSON. Abort (NO-GO) if the witness fails.
4. Cell-text audit: all four cell templates share an identical intro prefix and identical tail (MIDDLE + PUBLIC_INPUT); every pairwise difference confined to the A/B slot region; template SHA-256 values recorded.
5. Provider health: one 16-token AUTH_SMOKE probe through the exact provider code path, executed at step zero before the freeze commit is consumed by sessions, logged `AUTH_SMOKE, non-evidence` in `preflight/`; plus a metadata-only `/models` attest. No further non-experiment generation calls.

## 6. Terminal states, retention, halt rule

- Terminal states restricted to the project enum: SUCCESS · ORACLE_FAIL · TIMEOUT · AGENT_GIVEUP · MODEL_REFUSAL · TOOL_FAILURE · PROVIDER_UNAVAILABLE · HARNESS_ERROR. Operational mapping (fixed here, prespecified): oracle-rejected final submission → ORACLE_FAIL; no parseable submission in the allowed turns → AGENT_GIVEUP; submitted program exceeded the 20 s execution timeout on its final rejection → TIMEOUT; explicit model refusal text → MODEL_REFUSAL; execution-infrastructure fault → TOOL_FAILURE; provider-side failure on any turn → PROVIDER_UNAVAILABLE (infrastructure, not task failure; session terminal, retained, never retried); unexpected harness exception → HARNESS_ERROR.
- Every failure retained; no retries; no seed replacement; no arm expansion without a prereg amendment recorded before execution.
- Halt rule: if 3 consecutive sessions terminate PROVIDER_UNAVAILABLE, the phase stops (provider outage), retaining all records, and reports status halted.
- Budget: per-call token usage and estimated cost appended to `sp2027/research_execution/BUDGET_LEDGER.jsonl` (one JSONL line per call; AUTH_SMOKE line labeled non-evidence). Pricing basis: USD 3/M input + 15/M output (same basis as prior ledger entries). Phase projection at worst case (32 calls × ~750 in / 1400 out tokens): ≈ $0.75 estimated, far below the $5 phase ceiling; project guardrails $50 alert / $200 hard stop remain in force.

## 7. Predictions and falsifiers (prespecified)

- P1 (primary): R+ cells (C1, C3) accepted more often than R− cells (C2, C4) on matched seeds — the P010 premise finding generalizes to RC4.
- P2: naming (A) has no detectable effect on acceptance given fixed B (|C1 vs C3| and |C2 vs C4| small), consistent with the public JSON retaining `algorithm`/`keystream_reuse` labels.
- F1: if C4 succeeds about as often as C1, the premise is not load-bearing for this fixture — an honest null that weakens the P010 generalization claim. Operationalization (prespecified): |accepted(C4) − accepted(C1)| ≤ 1 on executed matched sessions (per-cell n=4).
- F2: if C3 fails while C1 succeeds on matched seeds, naming contributes on RC4 (contradicting the P010 naming-null). Operationalization: accepted(C3) = 0 while accepted(C1) > 0.
- F3: if C2 succeeds on any seed, the all-zero-reference sentence is not necessary under the derive-from-observations frame. Operationalization: accepted(C2) > 0.
- Failure stages recorded (parse / policy / execution / execution_timeout / oracle) for every rejected submission.

## 8. Analysis plan

- Per-cell exact counts: sessions, accepted, submissions, turns, failure stages.
- Paired-by-seed table across the four cells.
- Marginal contrasts B+ (8 sessions) vs B− (8) and A+ vs A− with Fisher exact one-sided and two-sided p (descriptive; hand-computed hypergeometric; no alpha threshold claim).
- Paired discordance C1 vs C4 (exact binomial two-sided) and C3 vs C2 (descriptive).
- Explicit statement: n=16 detects only large effects; results are mechanism-identification evidence for one model label, one fixture family, one contract; no capability-rate or generalization claim; **never pooled with P010** — P010 numbers are reported side by side only (comparison table at the end of REPORT.md, generated from P010's frozen `summary.json` read-only).
- REPORT.md in English, ending with the side-by-side comparison table against P010.

## 9. Retention, integrity, provenance

- All raw provider responses, prompts, execution captures, and events retained verbatim; failed sessions retained.
- Parameters frozen: `max_tokens=1400`; provider default temperature (not set); provider call timeout 300 s; execution timeout 20 s.
- Freeze before outcomes: `FREEZE.json` (SHA-256 of every prompt/fixture/policy file) + `PROMPT_HASHES.json` (per-cell template hashes and per-(seed,cell) turn-1 prompt hashes; turn-2 prompts depend on observed feedback and are hashed at session time in `events.jsonl`) are written and git-committed BEFORE the first experimental provider call. Preflight outputs are produced after the freeze commit and hashed in the final integrity manifest.
- After completion: leak scan (no prompt may contain any seed's truth or key material), `hashes/all_artifacts.sha256` snapshot, `STATUS_INFO_CONTRACT_RC4.json`, `FINAL_FREEZE.json`; no post-hoc edits to artifacts.
- Model identity is provider-attested only (no weight verification); recorded with every artifact.
- Scope: the runner stores full prompt text and execution stdout per turn as forensic captures; these are post-hoc records not visible to the model and do not alter model-visible content.

## 10. Non-pooling declaration

This protocol creates a new, separately versioned prospective cohort. It does not modify, replace, or re-label any historical or protected artifact; P010 (`info_contract_2x2_20261018/`) is read-only. Nothing under `sp2027/paper/` is touched.
