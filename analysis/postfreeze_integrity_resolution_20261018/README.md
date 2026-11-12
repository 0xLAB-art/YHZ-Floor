# Postfreeze artifact integrity resolution — 2026-10-18

Independent integrity verification of the postfreeze novelty-program corpus (the provenance-verified
program described in `/tmp/opencode/novelty_program/20261017_master/AUDIT_LEDGER.md`), performed as
part of the ACTS-Attack completion mission. Two objectives:

1. Resolve a candidate-identity discrepancy discovered in `surrogate_conversion_20261017_attempt3`:
   the archived `surrogate/generated_agent.py` did not match the hash recorded before/after execution.
2. Sweep every hash manifest in the corpus (v2, base-corrected) and classify each discrepancy.

No protected or archived file was modified. This directory is a new versioned record.

## Summary of results

- **Executed candidate recovered bit-exactly.** The fence-body of the direct-generator transcript
  (2,603 chars, 68 lines) hashes to `a5e8ed51…` — exactly the recorded pre-execution hash
  (`candidate_generation_record.json`) and the post-execution snapshot (`hashes/all_artifacts.sha256`).
  Replayed against the recorded oracle replies, it reproduces the accepted run **bit-exactly**
  (9,640 queries, zero divergence, claim-object hash `919ca521…` = `run_result.json:candidate_sha256`).
  → The surrogate arm's SUCCESS classification stands on hash-proven executed bytes.
- **Archived path misrepresents the executed candidate.** The on-disk `generated_agent.py`
  (`4fbd70a0…`, 248 lines, mtime 08:20:57) is a post-run replacement (full-scan variant, ~20,485
  queries live), written 27 s after the hash snapshot and 54 s after the run. It is a functioning
  solver but was not the executed program.
- **Corpus-wide sweep: 69 manifests / 733 entries. 719 match (+1 hardlink dup); 13 flagged
  anomalies, ALL resolved.** Exactly one anomaly is content-level on an executed artifact (the
  attempt3 candidate file above). All others are snapshot-ordering or hashing-convention artifacts,
  each proven below. Zero genuinely missing files.

## Part 1 — attempt3 candidate-identity defect (fully characterized)

Timeline (UTC+03), attempt root
`sp2027/paper/capability_merge_20261016/artifact_documentation/novelty_program_20261017/surrogate_conversion_20261017_attempt3/`:

| time | event |
|---|---|
| 08:16:41–08:19:30 | `direct_generator` session (opencode CLI, model `opencode/glm-5.3-flash-free`) returns one compact program block between `CODE_BEGIN`/`CODE_END`; prompt required "under 120 lines", no tools. |
| 08:20:01 | `surrogate/candidate_generation_record.json` records `candidate_sha256 = a5e8ed51…` (pre-execution freeze). |
| 08:20:03 | `surrogate/run_surrogate.py` executes the candidate against the local oracle; `run_result.json` verdict success, 9,640 oracle queries, `candidate_sha256 919ca521…` (that field is the **claim-object** hash: `sha256(json.dumps(claim,sort_keys=True))`, run_surrogate.py line 47). |
| 08:20:30 | `hashes/all_artifacts.sha256` snapshot records `a5e8ed51… surrogate/generated_agent.py`. |
| 08:20:57 | `surrogate/generated_agent.py` mtime — content replaced with `4fbd70a0…` (248 lines, expanded full-scan variant). |

Verification chain:

- **Extraction** (`evidence/extract_candidate.py`): regex `CODE_BEGIN(.*?)CODE_END` → strip ` ```python `
  fences → body sha256 = `a5e8ed51…` (= recorded hash). Variants tried and NOT matching: inner-stripped
  `c29cfca6…`, inner-as-is `c228737a…`, whole-text `b770b058…`.
- **Replay** (`evidence/replay_candidate.py` → `evidence/replay_results.json`):
  - (A) agent transcript: 9,640 queries + one CLAIM; claim-object sha `919ca521…` = run_result.candidate_sha256.
  - (B) oracle transcript: 9,640 queries, identical sequence; 9,637 unique; 3 duplicates; 0 contradictions.
  - (C) reconstructed candidate vs recorded replies: `full_match = TRUE` (9,640 queries, no divergence, claim exact).
  - (D) archived candidate vs recorded stream: **diverges at query 0**.
  - (E) live grading on fresh secrets: reconstructed → SUCCESS at 9,619 queries; archived → SUCCESS at 20,485 queries (~2.1× budget; matches full-scan design 5 blocks × 16 × 256 + probes).
- **Archived file characterization**: no key/plaintext material; functioning early-no-break `sweep()`
  full-scan variant with perturbation-probe disambiguation and `OracleDead` degradation; reads
  `ct_hex OR ciphertext_hex`. The defect is version-control, not truth-boundary.

Implications: cite the surrogate candidate ONLY via `evidence/executed_candidate_reconstructed.py`
(byte-exact, hash-proven). Do not use the archived path as executed bytes. The accepted result is
independently reproducible from retained transcripts.

## Part 2 — attempt4 secret-hash semantics (resolved: no defect)

`hashes/secret_hashes.sha256` records `599913253f… development.secret` and `84039181… heldout.secret`.
Convention (src/run_experiment.py + src/independent_oracle.py): secrets are written as `value + "\n"`
(9 bytes on disk); the recorded hash is `sha256(value.strip())` over the 8-char value; the oracle
compares stripped candidate vs stripped expected and its `expected_value_hash` uses the same value-hash.

Numeric proof: `sha256(strip(truth_material/development.secret)) = 599913253f…` ✓ and
`sha256(strip(truth_material/heldout.secret)) = 84039181…` ✓. Raw file-byte hashes are
`bc68bb03…` / `b1fcbbd5…` (the values my sweep initially flagged). Candidate files contain the
exact 8-byte value (`candidate_sha256 = expected_value_hash` by construction).

## Part 3 — attempt4 manifest/frozen_inputs ordering (resolved: no defect)

`hashes/frozen_inputs.sha256` records `ba52ba8c… manifest.json`; current `manifest.json` is
`1f1f811a…` (the hash cited in AUDIT_LEDGER as attempt4's manifest). Reconstruction proof: removing
the three finalizer fields (`completion_status`, `integrity_gate`, `claim_allowed`) reproduces
`ba52ba8c…`; the current file reproduces `1f1f811a…`. I.e., the finalizer appended completion
fields after `frozen_inputs` was written. Benign ordering.

## Part 4 — corpus-wide sweep v2 (base-corrected)

Method (`evidence/integrity_sweep_v2.py`): resolve each manifest entry against base = parent of
`hashes/` when the manifest sits in a `hashes/` dir, else the manifest's own dir; absolute entries
as-is; hardlink-dedup; classify MATCH / MATCH_DUP / SELF_STALE / EMPTY_AT_SNAPSHOT / MISMATCH / MISSING.

Global: **MATCH 718 + MATCH_DUP 1; SELF_STALE 3; MISMATCH 4; MISSING 6; EMPTY_AT_SNAPSHOT 1** (~733
entries, 69 manifests). Every flagged item:

| # | item | class | resolution |
|---|---|---|---|
| 1 | attempt3 `surrogate/generated_agent.py` rec `a5e8ed51` vs act `4fbd70a0` | MISSING-equivalent MISMATCH | **content-level defect** — Part 1; executed bytes recovered; replay-exact |
| 2 | attempt4 `manifest.json` rec `ba52ba8c` vs act `1f1f811a` | MISMATCH | finalization ordering — Part 3 |
| 3 | attempt4 `hashes/secret_hashes.sha256` bare names | MISMATCH | strip convention — Part 2 |
| 4 | attempt2 `control/proxy.py` rec `02bf3648` vs act `dcddfc43` (mtime 07:44:51) + `control_oracle.jsonl` empty at snapshot | MISMATCH + EMPTY_AT_SNAPSHOT | snapshot taken at control-run start; proxy edited after snapshot; non-duplicating timing artifacts |
| 5 | scale_pilot `preflight/hashes.sha256` 4 entries | MISSING (base) | files exist at attempt root; **all 4 hashes match exactly** (`1c7767754a…`, `c6062e1472…`, `c88de6c9cc…`, `d9a28a1384…`) |
| 6 | retry1 `retry1_artifacts.sha256` line 17 self-hash `597a0def` vs current `98eaec2d` | SELF_STALE | manifest regenerated once; live and preserved copies byte-identical (3129 B, 19 lines); all content entries match |
| 7 | compositional `all_artifacts.sha256` (self `54cebd1c` vs `42adb8a1`) and `source_hashes.sha256` (self `dc2e032d` vs `b18d828c`) | SELF_STALE ×2 | self-hash refresh; all other entries match |

Net: **zero missing files; one content-level anomaly on an executed artifact (item 1), fully
resolved by hash-proof + replay; every other flag is bookkeeping.**

## Part 5 — remediation policy (recommended, forward-looking)

1. Freeze candidate bytes by hash at execution; never edit an executed artifact in place. Replacements
   get a NEW filename (e.g. `generated_agent.expanded.py`) plus a note.
2. Take snapshot manifests after finalizers; record the final manifest hash in the status file.
3. Record hash conventions in manifests (byte-hash vs value-hash; strip rules).
4. Treat `evidence/executed_candidate_reconstructed.py` as the canonical executed artifact for the
   surrogate arm; keep it immutable.

## Evidence files (this dossier)

- `evidence/executed_candidate_reconstructed.py` — sha256 `a5e8ed51…` (hash-proven executed candidate; bit-exact replay verified)
- `evidence/replay_results.json` — sha256 `85c76305…`
- `evidence/extract_candidate.py` — sha256 `0e33aa18…` ; `evidence/replay_candidate.py` — sha256 `b57e2716…`
- `evidence/integrity_sweep_v2.py` — sha256 `8fea9496…` ; `integrity_sweep_v2.json` — `f084c741…` ; `integrity_sweep_v2_out.txt` — `2a7f1949…`
- Source records (full hashes in SHA256SUMS): attempt3 `surrogate/{direct_generator_transcript.jsonl,
  candidate_generation_record.json, run_result.json, generated_agent.py}`, `hashes/all_artifacts.sha256`,
  `transcripts/surrogate_{agent,oracle}.jsonl`, `oracle/oracle.py`, `model_calls.json`,
  `control/{exact_control_record.json, executor.py}`; attempt4 `{manifest.json, records.json,
  hashes/secret_hashes.sha256, hashes/frozen_inputs.sha256, truth_material/*.secret}`.

## Reproduction

```
python3 evidence/extract_candidate.py <attempt3>/surrogate/direct_generator_transcript.jsonl
# → prints sha256 a5e8ed51… (must equal recorded pre/post-execution hash)

python3 evidence/replay_candidate.py
# → full_match TRUE; claim sha 919ca521… == run_result.json candidate_sha256
```
