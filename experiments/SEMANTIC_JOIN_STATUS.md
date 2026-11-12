# Remaining semantic joins

This is a bounded reconciliation record. It does not reopen every archive
member, convert external benchmark observations into ACTS trials, or pool any
denominators.

## WebSP-Eval

- The retained release re-check pins `wi-pi/webspeval_code` at commit
  `cc0bbc41166612432819719e95f3d53294037c83` and records the corresponding
  source-freeze archive receipt in `working/archives/archive_receipts.json`.
- The release contains datasets, ground-truth action files, replay code, and
  judges, but not the authors' paper-time trajectories, screenshots, logs, or
  per-task verdicts. Its own clock is a task cap, not a reported metric.
- Therefore the WebSP linkage is source-addressable for the evaluator audit,
  but the paper-result-to-run binding remains `cannot_reconstruct`; no WebSP
  result is an ACTS execution or a recoverable physical-run denominator.
- Targeted archive inspection counted 96 state-trace JSON files and no files
  matching paper-run trajectories, `agent.log`, `thoughts.json`,
  `interact_messages.json`, or run-output artifacts. The traces are released
  dataset/replay material, not the paper's evaluated trajectories.

## Cybench

- The source-freeze archive is content-addressed in
  `working/archives/archive_receipts.json` and the selected analytics members
  are hashed in `selected_result_metadata.json`.
- Targeted nested inspection found 9,734 archive members: 9,619 under the
  benchmark tree, 14 analytics members, 5 grading members, and 12 agent-output
  members. `analytics/metrics.csv` includes a serialized `challenge_results`
  object and `detail_metrics.csv` contains 11 challenge rows, so the artifact
  structure is more informative than a single aggregate row.
- The apparent agent outputs inspected in the archive are Git-LFS pointer
  stubs, not payloads; they do not bind the aggregate metrics to complete raw
  transcripts or generated programs.
- `analytics/metrics.csv` has one aggregate row with
  `total_subtasks=25`, `total_correct_subtasks=9`, `accuracy=36`,
  `total_tokens=234046`, `average_time_taken_ms=0`, `num_challenges=0`, and
  `total_time=891425.9963378906`. The zero and inconsistent clock fields are
  retained, not repaired. `metrics_filtered.csv` has 19 mixed grouped/detail
  rows; 19 is not a run count.
- The local Cybench review additionally establishes that the released
  harness computes flag equality inside the agent-controller process and that
  paper-time checkout identity is unresolved. The pinned release and the
  historical comparator are therefore mechanism evidence for evaluator-boundary
  analysis, not a reconstructed historical success rate.
- Time fields are syntactically labelled in milliseconds and challenge-level
  rows are recoverable, but the producing run, exact clock boundary, and
  complete raw-output payload are not jointly recoverable. The correct status
  is `PARTIAL_METRIC_STRUCTURE_BUT_PAPER_RUN_LINK_UNRESOLVED`.

## Archive scope

The 12-archive enumeration reached EOF and retains SHA-256 receipts. Targeted
nested inspection is now complete for the WebSP and Cybench archive roots, but
the missing LFS payloads and paper-time run binding remain unresolved. Archive
membership is not an ACTS physical execution. No pooled rate, causal estimate,
or stronger historical claim is licensed by this reconciliation.

Primary evidence: `working/archives/SCIENTIFIC_DISPOSITIONS.md`,
`working/archives/archive_receipts.json`,
`working/archives/selected_result_metadata.json`,
`sp2027/benchmarks/websp_eval/evidence/release_recheck.md`, and
`sp2027/benchmarks/cybench/fields.md`.

The exact receipt and selected-member hashes, counts, and current disposition
are machine-readable in `ARCHIVE_JOIN_AUDIT_20261018.json`. This recheck did
not change either evidence ceiling: WebSP remains paper-run-unresolved, and
Cybench remains producing-run/time-boundary-unresolved with LFS output
payloads unavailable.
