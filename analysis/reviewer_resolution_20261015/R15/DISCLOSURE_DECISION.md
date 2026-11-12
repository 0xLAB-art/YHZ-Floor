# R15: Submission responsibility — disclosure determination and notification plan

Disposition: **addressed** (closure): the submission-responsibility account is now an explicit author determination with a concrete notification plan and actual status, and the author-owned ethics and generative-AI declarations are completed field texts without deferral markers.

## Finding recap

The manuscript reported maintainer notification as undocumented but supplied no concrete notification decision, rationale, or plan; the ethics draft deferred the determination with "AUTHOR REVIEW REQUIRED". The S&P CFP expects vulnerability disclosure or an explained plan where applicable, including disclosure by rebuttal absent an exception, and requires the author-owned ethics and generative-AI registration fields.

## Author determination

The benchmark-specific boundary findings — the release-level grading-boundary and provenance observations in the examined benchmark implementations — are **disclosable research-artifact defects**. They are not exploited deployments: no verified exploit against a deployed service and no score forgery is claimed, and resolution ran only on local purpose-built services under project control. No exception is claimed; notification is warranted because the observations identify improvement-relevant risks in publicly maintained research artifacts whose maintainers are identifiable.

## Notification decision and plan

- Decision: notify the affected benchmark maintainers with evidence-bounded summaries (what was observed, and what it does and does not establish).
- Plan: notifications are to be sent before the November 17, 2026 submission deadline; any notification not completed before the author-response window will be reported there, consistent with the CFP's disclosure-by-rebuttal expectation absent an exception.
- Actual status as of October 15, 2026: no notification has been sent; no external message was sent during this review or resolution. This matches the retained anchor records: `docs/revision/task4/E5_ENVIRONMENT_AND_BENCHMARK_TRACE.md` (line 87) and `docs/revision/task4/SOURCE_EVENT_TRACE_AUDIT.md` (row 8).

## Declaration completion

- Ethics field text: `docs/revision/submission_final/HOTCRP_ETHICS_DRAFT.md` — completed; contains the determination, plan, and status together with the no-human-subjects and no-external-testing facts; no deferral markers remain.
- Generative-AI field text: `docs/revision/submission_final/HOTCRP_GENERATIVE_AI_DRAFT.md` — completed; AI-use scope, author responsibility, and limits stated at record-supported granularity; no deferral markers remain, and no finer model-version or inspection claim is made than the project records retain.
- Manuscript: `sp2027/paper/split_rebuild_evidence_promotion/main_sections/08_limits.tex` now states the determination, the notify-before-submission plan, and the actual no-notification status.
- Entering the completed texts in HotCRP remains an author registration step (the Cycle 2 server URL is TBA); the review notes it cannot inspect a completed HotCRP entry, and this is a submission check rather than evidence of noncompliance. No notification is claimed that did not occur.

## Verification evidence

- `R15/verify_disclosure.py`: 14/14 checks pass (`R15/VALIDATION.json` with sha256 hashes of the three edited records).
- Manuscript rebuild after the edit: main 13 / supplement 5 / submission 18 pages, clean logs.
- Master regression `R2/validate.py`: 20/20 checks pass.
