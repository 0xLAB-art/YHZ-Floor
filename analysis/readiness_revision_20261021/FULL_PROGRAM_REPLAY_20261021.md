# Full program replay and claim-scope repair — 2026-10-21

This follow-up supersedes the previous retained-output-only limitation for LOCAL executable replay. It does not mark the existing public artifact as complete or claim publication.

## What actually ran

All 852 retained H1-R3 session decisions were replayed with unchanged program bytes and public input bytes. Exactly 851 sources were admitted and launched; one retained syntax rejection was re-identified without falsely calling it executed. Of the launched programs, 849 completed with JSON-object output and two reproduced their recorded execution failures. The independently implemented reference oracle checked the fresh outputs against the synthetic fixture state outside the child sandbox.

Results:
- 801 accepted exploit recoveries.
- 20 correct abstentions, a different predicate.
- 28 completed but rejected recoveries.
- 2 execution failures.
- 1 syntax/source rejection.
- 852/852 verdict agreement; zero infrastructure errors.
- All parsed outputs, or their originally missing status, agree with the retained record.

The first full run is retained in fresh_execution_replay_v1/. The archive was then extracted under /tmp/acts_complete_portable_20261021/ and all decisions were replayed again from that extracted package. Its report, bound to the delivered runner SHA-256, is full_execution_portable_report.json. No API calls, regenerated model outputs, retries, replacement seeds, repaired candidate programs or enlarged model-session denominator were used.

## Delivery

Complete executable review package:
h1r3_complete_replay_v1.tar.gz
SHA-256: 20df039a623e9bf1a6feb40cccf4ef8fe7615ed369b4fbfc9979f67d25a55b39

Fresh execution witness:
h1r3_fresh_execution_witness_v1.tar.gz

Execution report:
full_execution_portable_report.json

The complete package includes the exact earlier retained evidence, the original independent oracle and qualification implementation, a new execution adapter, sandbox tests, commands and file manifests. The witness separately retains fresh execution records, source/input hashes, stdout/stderr, outputs, independent oracle results and hashes. Output directories are new and outside the retained corpus.

The sandbox mounts only the Python runtime, exact program and public observation file. Original responses, output, prompts, private truth, verifier and artifact directories are not mounted. Namespace and resource limits are stated in the README. Seven tests pass, including incorrect/missing output rejection, program-hash tampering, path traversal, read-only public input, host-file exclusion and host-loopback exclusion. These probes support the new setup only; they do not prove historical enforcement or exhaustive isolation.

## Manuscript changes

- Section 8 now distinguishes limited public dispositions from the separately staged full candidate and states the successful fresh replay counts. Original response regeneration remains unavailable. The public anonymity/publication limitation remains explicit.
- The missing period after “it reports no chain result” is fixed.
- Repeat-prompt controls is the manuscript term; the first occurrence explains that R4 is called noise controls in the registry. All 64 rows form 32 pairs with identical prompt hashes, verified from the frozen results. No registry labels were rewritten.
- Abstract, introductory claim, contribution, roadmap and conclusion explicitly scope equivalence to primary L3. The abstract and contribution/conclusion also identify the tested route/two-family scope. Secondary-level limitations remain intact.
- A duplicated census sentence was removed and the reproducibility paragraph tightened to keep the original page limit without shrinking fonts, margins or figures.

## Verification

Main: 13 pages including references. Supplement: 5. Combined: 18.
All 32 paper-number checks pass; all 41 references pass citation checks.
Protected research verification: 44/44, unchanged.
Completion validation: 34/35. The existing DOI/identity regex flag remains; no anonymity rule or scientific threshold was weakened.
Page 12 was visually inspected. No overfull boxes, undefined citations or undefined references were reported.

## Remaining boundary

The package is locally staged, not publicly published or approved for anonymous distribution. It preserves original local paths/provider metadata and deliberately includes synthetic secrets needed by the oracle. A public anonymous release still needs traceable redaction, distribution/licensing decisions and an actual hosted artifact link. The previous limited public dispositions were not silently replaced. Earlier paper reviewer bundles remain unsynchronized.

No independent benchmark experiment ran. Fresh execution on the original fixed tasks is reproducibility evidence, not external validation, another model trial or broader equivalence evidence.

Paper source baseline: /tmp/acts_full_replay_baseline_20261021/
Exact manuscript changes: FULL_REPLAY_CLAIM_REPAIR_20261021.patch
