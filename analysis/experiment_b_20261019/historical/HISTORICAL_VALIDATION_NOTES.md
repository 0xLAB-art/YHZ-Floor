# Historical Real-Defect Validation Notes — Experiment B (read-only)

Date: 2026-10-19. Scope: Experiment B protocol §9 (legitimate historical real-defect validation). Method: read-only inspection of immutable archives; offline recomputation (Python stdlib only, no network, no provider calls, no repo modifications; scratch in `/tmp/opencode/`). Rules applied: a historical defect is "independently demonstrated" only if the underlying raw evidence exists and the predicate can be recomputed; otherwise it is classified as label-only or incomplete with the limitation stated. No synthesized replacements; no pooling of incompatible cohorts.

## Summary determination

Across the inspected archives, **no historical instance of a false-promotion defect (HEB-1 / IAR-class) was found**. The genuine evaluator-boundary failures found and recomputed are of the **observation-validity class**: a qualification-policy contradiction that blocked every compliant candidate from execution, and a serialization crash that aborted the pipeline and left a masking terminal record. These defects prevent measurement; they cannot and did not inflate any claim. Denominators are recorded below; full recomputation was performed for the free_v2 campaign (RV-1, RV-2); the repair-gate pair was partially recomputed (RV-3); other candidate items are classified honestly as partially verified or archival-label-only.

Campaign history context (for reading the records): paid pilot run 2026-10-18 18:17 (72/72 `PROVIDER_FAILURE`, HTTP 401) → free_v2 run 18:53 (72/72 `HARNESS_FAILURE`) → offline repairs → deterministic gate pair 20:06 → replacement pilot. This note covers the 18:17–20:06 records.

---

## RV-1. free_v2 serialization crash (raw-recomputable; recomputed)

- Record: `contract_sound_agent_pilot_20261018_free_v2/pilot_results.json` (sha256 `44ca08103e134b676e84b3e48f255b9b…`), 72 rows, all status `HARNESS_FAILURE` with the single error string `TypeError:Object of type PosixPath is not JSON serializable`. Sample session: `sessions/contract-sound-001-087b5f465b46/session_result.json` (sha256 `dec7b40252579524e1c3b2ba7204d555…`): `{"error":"TypeError:Object of type PosixPath is not JSON serializable","latency_s":7.517,"status":"HARNESS_FAILURE"}`.
- Root cause (driver `run_contract_sound_agent_pilot_free_v2.py`, sha256 `7c81945d3e6d26bc75f9ddb66eb47f87…`, lines 194/196): the `bundle` variable holds a `PosixPath`; `invoke_json(REFERENCE, bundle)` then calls `json.dumps(payload)` on that `PosixPath` → `TypeError`. Reproduced exactly offline: `json.dumps(Path('x'))` raises the identical message.
- Consequence: the pipeline aborted before the reference verifier and validator ran on any of the 72 sessions. The terminal record states only `HARNESS_FAILURE` and does not state that the candidate had been policy-rejected and never executed — the true stage is recoverable only by forensic recomputation (classification `HARNESS_SERIALIZATION_BEFORE_ORACLE` in the forensic matrix).
- Corroborating: the audit's `reference_invoked:true` for ordinal 1 corresponds to a manual forensic re-run at 19:02 (`manual_ref.stderr`: reference verifier v2 crashed `FileNotFoundError` because `candidate_output.json` was missing, line 123 `Path(bundle["candidate_path"]).read_text()`), not to the original pipeline.
- Repair: `contract_sound_repaired_pipeline.py` (sha256 `5d264dd19d692626079712607b16172a…`) passes `str(bundle_path)` as argv and returns structured `FAILED`/`INVALID_OUTPUT` records instead of raising; tests `test_contract_sound_repaired_pipeline.py` (sha256 `e64f8f1efddbea286f57e9dc7fee2dbf…`) assert the serialization failure mode is gone (`'PosixPath' not in json.dumps(...)`).

## RV-2. free_v2 qualification policy contradicts the declared interface (raw-recomputable; recomputed)

- Old rule (`safe_source`, driver lines 42–53, copied verbatim for recomputation): import allowlist `{json, sys, base64}`; any `ast.Call`/`ast.Attribute` node containing token `open(` (among `subprocess, socket, requests, urllib, os., open(, __import__`) is `disallowed-boundary`; first violation in `ast.walk` order wins.
- Recomputed verdicts over all 72 extracted candidates (first-python-fence extraction independently verified against `candidate.py` and the matrix `extracted_source_sha256`, 72/72 match): **72/72 rejected** — 71× `disallowed-boundary`, 1× `disallowed-import` (session `contract-sound-005-1f13f6e4cd6e`, line 3 `from hashlib import sha256`; matrix record sha256 of source `acc4a84ff04c4b6f25bc81c289117e39f2e179688e2030f1f0ccee1abc658fc4`).
- The prompt (`neutral_prompt` in `validate_72_repair_deterministic.py`) instructs: "The harness will execute it as: `python -I candidate.py public_instance.json`. Read only argv[1], parse JSON, and print exactly one JSON object on stdout." With the allowlist `{json, sys, base64}` there is no way to read argv[1] other than `open(...)` — which the scanner bans. **The official prompt and the official policy are mutually unsatisfiable for any compliant solution.** Every candidate was blocked from execution; `target_effect` was always `NOT_OBSERVED`; a perfect solution would have been scored invalid.
- Repaired rule (same module as RV-1): accepts read-only `open(sys.argv[1])` / `open(sys.argv[1], "r"|"rt")` only (strict AST shape), collects all violations. Recomputed verdicts over the same 72 candidates: **71/72 `QUALIFIED`; 1/72 rejected** (same session 005, rule `disallowed-import-from`, value `hashlib`, line 3). Session 001: old `(False, 'disallowed-boundary')` → new `(True, 'QUALIFIED')`.
- Residual note: `hashlib` remains outside the repaired allowlist (defensible under the declared restricted subset: the task needs only json parse/print via `json`/`sys`/`base64`), but it is a still-open interface-vs-prompt question for that single session, not a recomputed contradiction like the `open(` case.
- Matrix taxonomy: `contract_sound_agent_forensic_matrix_20261018/FORENSIC_CLASSIFICATION_MATRIX.json` (sha256 `d4cfc1a224b15eb3fe453fc5e76039ac…`) records 71× `disallowed-boundary` + 1× `disallowed-boundary;disallowed-import-from`. The combined string cannot be emitted by the driver rule (single-token early return); the verbatim recompute above is authoritative for the driver's own behavior.

## RV-3. Repair deterministic gate, failed → passed pair (partially recomputable)

- PASSED record: `contract_sound_72_repair_deterministic_20261018/REPAIR_DETERMINISTIC_GATE.json`, sha256 `63aeca2ab9157987ce9e2d69ed7cd3c1cacdf5719a8a39597d139cf2eed67b0f`; status `PASS_DETERMINISTIC_GATE`; 36/36 pair checks pass; provider/network calls 0; schedule seed 20261019. **Independently re-executed** offline from the retained validator revision (`validate_72_repair_deterministic.py`, sha256 `27987d6ec093fafb0e908ef248c5178a…`, with output path redirected to `/tmp/opencode/`): produced JSON byte-identical to the preserved record.
- FAILED record (preserved): `contract_sound_72_repair_deterministic_20261018_gate-failed-raw-order-check/REPAIR_DETERMINISTIC_GATE.json`, sha256 `da4cddf9e34238817d525d9d07cb0a22ef9b831c8cf28407ad67dd1aaa506eee`; status `FAIL_DETERMINISTIC_GATE`; 36/36 pairs fail exactly one check `raw_representation_distinct`; every other field (instances, prompts, canonical hashes, schedule) byte-identical to the passed variant.
- Semantics: the check requires the order-sensitive raw serialization of the reordered representation to differ from the original (`json.dumps(..., sort_keys=False)` inequality); the failed run is consistent with a pre-fix identity/no-op reorder. The pre-fix validator revision was not retained, so the exact failing binary cannot be re-run; the failure predicate is recomputable in principle, and the fixed revision's pass is verified byte-identically. Classification: construction-QA defect caught by the campaign's own deterministic gate, then fixed — it demonstrates repair-process integrity, not an evaluator-boundary false-attribution defect.

## Candidate items from the canonical audit (classification; no overclaim)

### C-1. E5 escrow / "verifier-hash, launcher metadata" (raw records exist; record-level verification performed)
- `E5_RAW_RUN_CENSUS_20261018.json` (sha256 `bccd7a5dbd0648cbb37b6fa3820e0143…`) and `.md`: 29 canonical retained records `{ORACLE_FAIL 9, PROVIDER_UNAVAILABLE 15, SUCCESS 1, TOOL_FAILURE 4}`; partition 14 graded (1/14 accepted; 15 provider-unavailable retained separately).
- Recompute performed: the single SUCCESS record path resolves on disk (`sp2027/agent-eval/runs_e5/session_r30/runs/e5_R30__e5_aes_key_recovery__T1_known__rep1.json`) and its sha256 recomputes exactly to the census value `0fc09afb2798353158fcc24264c168f8320ceb8eb2bfecaa8611ed032679f1f4`. Record content: `oracle.implementation_sha256 = 1b58b952…`, `separate_process: true`, `ground_truth_channel: reserved`, verdict success with `observed_value: candidate_sha256=… escrow_seq=3`, `oracle_queries: 0`, and a retained `failure_reason: "run 2: no CLAIM line (exit 0)"` inside a success verdict (mixed attempt metadata); `environment` block captures host Python/platform/Docker; `provenance.validator_version = "acts-audit 0.1.0"`.
- Classification: raw evidence exists; census/count and record hash **independently verified**; the audit's full characterization ("host-executed code, missing caller authentication, verifier-hash/launcher metadata defect") involves code-architectural claims beyond this record — **partially recomputed, limitation stated**. Not a false-promotion instance (defect concerns observation/attribution metadata provenance).

### C-2. H1 V2 response-only instrument ("XOR scorer defect retained")
- Raw corpus located and counted: `sp2027/analysis/checkpoint007_active_experiments/runs_009/revalidation_v2/raw_provider_responses` — exactly 90 payload files = 9 arms × 10 (`ecdsa_named/unnamed/undet`, `rc4_*`, `xor_*`), matching the audit's "90 provider responses".
- Derived records on disk: `research_execution/H1_V2_FAILURE_STAGE_SUMMARY.json` (sha256 `5a74c53f4d22db246c52f1377dc99a46…`): 90 raw, 81/90 strict top-level JSON parseable, 35/60 sufficient-condition candidate submissions, 0 oracle recoveries, 30/30 correct underdetermination; `H1_V2_FAILURE_STAGE_AUDIT.md` states the audit reads all 90 payloads and rules out provider delivery failure.
- Classification: raw corpus located and census-verified; the defect statements from the canonical audit ("40 attempts is not 35 candidate-bearing responses; XOR scorer defect retained") are **archival-audit statements not recomputed in this pass** (scorer recomputation possible in principle over the retained corpus; not performed — limitation stated). Not a false-promotion instance.

### C-3. Held-out prefix fixture, attempt 3 integrity failure
- Canonical audit: attempt 3 was 4/4 integrity-failed and excluded; attempt 4 (2 dev + 2 held-out cells) passed with its own manifest. Classification: **archival-label-only in this pass** (not independently re-inspected; no synthesized conclusions).

### C-4. Original paid pilot (context row)
- `contract_sound_agent_pilot_20261018/pilot_results.json` (sha256 `4d9c38729ea49be12671f1171cef9baa…`): 72/72 `PROVIDER_FAILURE`, error `HTTP 401`, `estimated_cost_usd: 0.0`, `no_retries: true`. Provider-access failure, not an evaluator-boundary defect; recorded here so the campaign history is complete and to prevent double-counting.

---

## Evidence-class table

| Item | Class | Recompute performed |
|---|---|---|
| RV-1 free_v2 serialization crash | raw-recomputable | error reproduced exactly; fix verified by tests present on disk |
| RV-2 free_v2 policy contradiction | raw-recomputable | 72/72 old reject; 71/72 repaired accept; prompt-policy unsatisfiability established |
| RV-3 deterministic gate pair | partially recomputable | passed variant re-executed byte-identically; pre-fix revision not retained |
| C-1 E5 escrow record | raw verified at record level | census hash match recomputed; full defect predicate partially |
| C-2 H1 V2 instrument | raw corpus located & counted | scorer/denominator predicate not recomputed |
| C-3 held-out attempt 3 | archival-label-only | none in this pass |
| C-4 paid pilot 401s | excluded (provider access) | status counts recomputed |

## Bottom line

1. The historical validation **did find genuine evaluator-boundary failures** — both in the free_v2 campaign (RV-1, RV-2), independently recomputed from immutable records, plus the internally caught and fixed deterministic-gate defect (RV-3).
2. Both genuine defects are **observation-validity class** failures (policy false-rejection of the declared interface; serialization crash with a masking terminal record). They produced **0/72 evaluator outcomes** and therefore no false promotion; they cannot support and do not constitute a HEB-1/IAR-style attribution defect.
3. No inspected historical record shows a false promotion of an unsupported claim. The HEB-1/IAR false-attribution mechanism was measured in the synthetic IAR-B/IAR-C experiments, not observed in historical runs — this is the honest negative/mixed result.
4. Limitations recorded: single-author inspection; recomputation limited to what raw evidence permits (C-1 partial, C-2 not recomputed, C-3 not inspected); the failed gate revision was not retained; no synthesized replacements were used; no cohorts were pooled.
