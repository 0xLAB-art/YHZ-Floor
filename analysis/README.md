# analysis/ — the campaign's working trees

This directory is the **working archive of the audit campaign**, served verbatim: the
analysis trees the frozen records were produced by, the evaluators that graded them,
and the forensic records that resolved questions along the way. It is provenance, not
curated reading — start from the [README](../README.md) or the
[experiments index](../experiments/INDEX.md) unless you are tracing how a result was made.

## What lives here

| Area | Directories | What they carry |
|---|---|---|
| The E2/E5/RQ4 trees | `acts_next_phase_20261019*/`, `readiness_revision_20261021/` | the attribution-ablation cases, mutation rosters, and the H1-R3 portable replay validation (`execute_replay.py`) |
| Evaluators + shared state | `artifact_access_20261022/`, top-level `*.py` | the grader implementations, `offline_checks.py`, `CLAIMS.json`, and the access audit |
| Wave forensics | `W3_FILL_*`, `CANONICAL_RUN_AUDIT_*`, `COMPLETE_EXPERIMENT_COVERAGE_AUDIT_*`, … | the dated audit documents: coverage maps, repair protocols, disposition records |
| Stage deliverables | `acts_next_phase_20261019/deliverables/`, `stage0/` | the trust-boundary maps, prior-art matrices, and reproduction reports from the campaign's phase gates |

Names are kept exactly as the campaign used them (dated, ALL-CAPS where they were
ALL-CAPS) — renaming working records would break the provenance the bundle exists to
serve. The curated, reader-facing projection of this material lives in
[`reviewer_bundle/`](../reviewer_bundle/).

## Executing anything here

Nothing in this directory should be executed outside isolation. The sandboxed replay
entry point is `reviewer_bundle/h1r3/h1r3_complete_replay_v1/execute_replay.py`; see
[SECURITY.md](../SECURITY.md) for the handling policy.
