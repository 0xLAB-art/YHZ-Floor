# Anonymous review distribution handoff

The author selected anonymous review distribution with identifying originals separated from the publication candidate. Nothing was uploaded or published. No experimental evaluations, retained attack programs, mutation tests or hosted-model requests ran during preparation.

## Distribution split

- `sp2027/artifacts/reviewer_full_candidate_20261022_v2/`: private original evidence and sources, including identifying signed RQ3 records and declared-author manuscript sources. Integrity verified over 22,358 manifest-listed files. Do not distribute as anonymous.
- `sp2027/artifacts/reviewer_anonymous_candidate_20261022/`: byte-preserving H1-R3 component, anonymous ablation source/evidence trees, matching historical fixed-executor records and anonymous PDF. Its archive normalizes owner and group metadata. Its own README states the exact exclusions.

The anonymous projection excludes identifying signed property-check records and original in-toto runner sources. Those originals were neither redacted nor re-signed. Full property/in-toto reproduction remains restricted to the private evidence, so the anonymous projection does not close every reproducibility gap. It does materially expand access to the central retained-program evidence beyond the reduced public repository.

## Fixed-executor provenance resolution

The later `artifact_documentation/reruns_20261016/fixed_executor/operation_records.jsonl` has twelve successes but clocks different from the manuscript. It remains unchanged in the private v2 candidate, whose census reports that finding.

The historical `sp2027/paper/anonymous_reviewer_artifact_v23/LEGACY_STUDY/results_rerun/operation_records.jsonl` has twelve recorded successes. Its executor-clock medians match the manuscript exactly before rounding: RC4 0.214196 ms, ChaCha20 0.131647 ms, CBC 1981.556789 ms, ECDSA 6.956233 ms. This historical cohort is supplied separately in the anonymous projection. No trials were pooled and no fresh operation was executed. Matching recorded timing does not independently re-establish cryptographic success.

## Verification scope

The prior full H1-R3 execution validation applies to the original retained component, not to a fresh end-to-end run of the new distribution. The new adapters remain unexecuted. Packaging unit tests passed 6/6. The anonymous PDF metadata has an empty Author field and 18 US-Letter pages. Identity scanning checks known direct identifiers; it is not a guarantee against all possible contextual identification.

The manifest verification receipt and archive checksum are stored beside this handoff and the archive respectively. External hosting and a manuscript availability URL still require an actual distribution action; no public availability claim was added.

## W7 refresh — 2026-11-11 (v3)

- `sp2027/artifacts/reviewer_full_candidate_20261111_v3/` (170 MB, 26,550 manifest files): the v2 selection plus the external-boundary wave evidence the paper now cites — Amendment-1 regrade lab, Amendment-3/4/5 admission records, the C1 confirmatory review, and the M1 published-protocol audit (external_published_audit_20261110: 60 registered sessions, amendments, ERRATUM_accepted_c2, M1_FINAL_RESULTS). Same exclusions and review profile as v2 (2 synthetic private-key files, provider records, historical paths); not anonymous-release-ready by design.
- `sp2027/artifacts/reviewer_anonymous_candidate_20261111/` (150 MB, 24,023 manifest files) + `reviewer_anonymous_candidate_20261111.tar.gz` (54 MB, sha256 84da7a98498a258eb78e6b37317a5b1bff595fffdbb69e601131683eb723b847 (final: carries the five ProReviewer-gap fixes)): the anonymous projection with the wave trees included. Integrity verify PASS (0 errors); direct-identifier scan 0 hits across 8 needles; PDF author field empty; no experimental rerun during packaging.
- `submission_evidence_20261022.pdf` inside both candidates is the current 36-page canonical build (sha256 a4ac4bb3…); the paper source tarball `acts_attack_evidence_source_20261022.tar.gz` was regenerated from the compile-verified arXiv source set (61 files) after the W7 page-state work.
- Builders: `build_candidate_v3.py` / `build_anonymous_v3.py` (byte-preserving discipline unchanged from v2). Hosting and the manuscript availability URL remain author actions (W4); nothing was uploaded or published.
