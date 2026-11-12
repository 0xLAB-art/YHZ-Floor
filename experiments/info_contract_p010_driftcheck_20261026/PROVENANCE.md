# P010 Drift-Check Rerun — Provenance

**Launched:** 2026-10-26 (UTC), after the powered cohort (seeds 101–108) and the
second-label replication (seeds 111–118) were already known.

**Purpose.** The original P010 cohort (seeds 41–44) read C2 at 4/4 while the
powered cohort read C2 at 0/8. Two explanations fit: (a) *seed heterogeneity* —
the eight powered seeds simply differ from the original four; (b) *temporal
drift* — the served model or harness environment changed between 2026-10-18 and
now. Re-running the ORIGINAL seeds 41–44 under the SAME protocol and label
separates them: reproduction of the original cell counts supports (a); a
changed C2 supports (b).

**Same-label conditions held fixed.**
- Base runner `run_info_contract_2x2_chacha20.py` is byte-identical to the
  original cohort's runner (loaded as a module; only the output namespace is
  patched — the same mechanism the powered cohort used).
- Protocol string `P010-INFO-CONTRACT-2X2-CHACHA20-v1`, prompt slots, Latin
  square, fixture/oracle/policy/feedback, max_tokens=1400, temperature unset
  (provider default) — all inherited unchanged from the base module.
- Model label `claude-sonnet-4-6-free` via `https://api.apmix.ai`, key at
  `~/.config/acts007/apmix.key` (route verified with a 1-token probe before
  launch).
- Seeds 41,42,43,44 (the original P010 seeds), 4 cells, 16 sessions, 2-turn
  flow with the same rejection feedback text.

**Epistemic status.** Reproducibility rerun, NOT a new pre-specified
cohort and NOT confirmatory. It is not pooled with P010, P010P, or P010L2.
The paper's registered numbers are untouched by this run; any statement
drawn from it will be labeled post hoc.

**Resume.** `results.jsonl` sessions are skipped on restart (same pattern
as the powered cohort runner).
