# Analysis validation report

## Immutable-source and population checks

- V4-02 schedule rows: 12; unique run IDs: 12; unique entry IDs: 12.
- Physical raw records: 12; retained transcripts: 12.
- Terminal census: {'ORACLE_FAIL': 4, 'SUCCESS': 8}.
- Successful sessions with explicit accepted verdicts: 8/8; failure sessions with explicit rejection verdicts: 4/4.
- Timing rows: 8; all have finite nonnegative integer T_M: True.
- The 11 source hashes frozen in the V4 manifest match current files; EXP-035 image digest was verified against local Docker image metadata without a build.
- Raw records are read-only inputs; no existing scientific result or lock is rewritten.

## Lock checks

`results_lock_h1pc.py` is the active successor lock checker and passed. It verifies public E1 H1=0/54, EXP-034 H1=0/12, EXP-035 H1=3/3 and arm accounting 35 mapped + 1 historical =36.

The predecessor `results_lock_v4.py` is retained as a historical check. It fails its predecessor hash assertion because `RESULTS_LOCK.json` current SHA-256 is `4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39`, not its expected `335ea2a10afe3cfe02ea8ee7d0f3aafeb3d63078ba5efc21c4fe1a10f06e50eb`. This is a predecessor-hash expectation mismatch, not evidence that the active H1PC successor lock failed. The historical script/lock is not modified.

## Freeze and manuscript status discrepancies

V4-02 manifest has `execution_status=FROZEN_NOT_LAUNCHED` and freeze metadata has `model_evaluation_started=false`, despite the retained 12-row V4 ledger, 12 raw records, 12 transcripts and successor lock. EXP-035 v2's manifest likewise says `FROZEN_NOT_LAUNCHED` while its three run records, H1 check and active successor lock establish 3/3. Both are retained metadata contradictions and were not changed.

`sp2027/paper/README.md` designates `sp2027/paper/main.tex` as the authoritative anonymous S&P manuscript, but README's claimed source hash and 13-page build are stale relative to the current root source/PDF (actual root PDF: 15 pages). The later `arxiv_preprint_20261014` source is a separate 18-page standalone preprint and contains V4/EXP-035. It is the newest evidence-integrated candidate, not the README-designated S&P source. Neither was modified.

## Remaining limits

The V4 timing values cannot be independently recomputed from raw monotonic endpoint readings because those readings were not serialized; only duration, session-bound UTC markers, code path and matching record/transcript are retained. Provider HTTP retries and token counts are not retained in V4. No manuscript was modified.

