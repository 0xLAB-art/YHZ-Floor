# ERRATUM 1 — the recorded `accepted_c2` field is unreliable when C1 fires first

**Found:** 2026-11-11, after the wave landed 60/60.

**Symptom:** all 10 `2018q-cry-lowe` rows read `"accepted": true,
"accepted_c2": false`, which would say C2 rejects a session C1 accepts — i.e.
the opposite of the F2 evaluator-invariance claim.

**Cause:** in the frozen runner's turn loop, the C1 branch `break`s out of the
turn loop before the `if c2 and not session["accepted_c2"]` bookkeeping runs.
A session solved in the same turn under both codings therefore records only
`accepted` and leaves `accepted_c2` at its default False.

**Scope:** session-level derived field only. The turn-level field
`oracle_match_c2` is computed before the branch and is correct.

**Verification (zero model calls):** the 10 affected rows all have a turn with
`oracle_match_c2: true`; sessions with a true turn-level C2 = 20, equal to
sessions with `accepted` = 20. The registered sweep recomputes every coding
from `turn_records`, so its C2 = 20/50 stands and no reported number changes.

**Rule:** read C2 (and C1) from `turn_records[*].oracle_match*`, never from the
session-level `accepted_c2` field, on every wave that used this runner.
