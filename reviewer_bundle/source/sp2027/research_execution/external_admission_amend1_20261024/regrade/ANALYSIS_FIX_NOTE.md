# ANALYSIS FIX NOTE — regrade_amend1.py post-freeze correction (2026-10-24)

The offline regrade script `regrade_amend1.py` was corrected AFTER the freeze
commit (`632b9139`) and BEFORE the outcomes commit. The fix touches ONLY the
offline analysis harness; no session, provider, prompt, fixture, or policy
input changed. Both regrade runs consumed the same 37 retained programs and
the same frozen policy snapshots (hash-asserted at runtime).

Defects fixed:

1. **Compare sandbox directory was never created** — `sandbox_stdout()` copied
   artifacts into `workdir` without `mkdir`, so every cleanup preservation
   compare raised FileNotFoundError and `output_preserved` was recorded `None`
   on all 17 edited programs (first regrade run). F3 was NOT evaluable in that
   state. Fixed with `workdir.mkdir(parents=True, exist_ok=True)`; the re-run
   executed all 17 compares and recorded `output_preserved: True` on 17/17
   (10 pairs both completed; 7 pairs both hit the 30 s sandbox timeout with
   empty identical stdout — recorded per-program as `orig_timed_out` /
   `clean_timed_out`).
2. **Rule-(c) acceptance formula** — a program qualifying under rule (b) with
   zero cleanup edits was incorrectly marked not-accepted under rule (c).
   Corrected to `accepts_c = qualified_b OR (edits>0 AND cleaned qualifies
   under b AND output preserved)`. Benign on this dataset (no program
   qualifies under (b): 0/37), but corrected for correctness of the record.

A `degeneracy_diagnostic` block was also added to the regrade output so a zero
movement is interpretable (0/37 programs qualify under rule (a) or (b); the
`open:not-readonly-argv1` boundary clause rejects every program).

Hashes: pre-fix `73defeeb685796ad25c230975325abf8fe8339699632443ca868f82cfa53f1b5`
(committed in the freeze manifest) → post-fix
`58bcc77a7686b066a3e747d16c1eeedf83a4aa55a0f92b585939eddb7a15af1d` (this
working tree). The frozen-session machinery (`run_amend1_sessions.py`,
prompts, fixtures, policies, client) is bit-identical to the freeze.
