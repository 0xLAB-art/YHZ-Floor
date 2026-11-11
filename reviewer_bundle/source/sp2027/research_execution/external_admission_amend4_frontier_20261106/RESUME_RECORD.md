# RESUME RECORD — Amendment 4

## Halt 1 (2026-11-07, after 11 sessions)

- **Trigger:** the registered halt rule (≥3 consecutive provider-side
  pre-output failures) on `2015q-cry-eps_part2` R0 slots of `gpt-5.6-sol`.
- **Diagnosis:** the failures are **HTTP 400 `content-blocked`** — the
  gateway's content filter rejects the eps_part2 prompts (9 BAD_RESPONSE
  events; up to 2 re-attempts per call recorded per the two-sided rule).
  Not a rate limit and not label exhaustion; the eps prompts (8 sessions)
  passed the same filter immediately before.
- **Disposition:** the 3 affected slots are recorded terminal
  PROVIDER_UNAVAILABLE rows and stay excluded from acceptance denominators
  per the registered two-sided rule (rows never deleted). The run resumes
  on the remaining plan order; the other two labels will attempt eps_part2
  with the same frozen prompts — whether the filter is label-independent is
  itself recorded. 16 calls / 20,104 input + 29,502 output tokens at halt.
- **Early measurement note (not a verdict):** all 8 completed eps sessions
  of `gpt-5.6-sol` (R0 and RT alike) are C2-accepted (first flag token ==
  pin) and C1-rejected (whole-stdout rule) — the Amendment-3 eps
  R0→RT collapse does not reproduce on this label so far; both codings
  remain live and the registered F1 is evaluated per coding at the end.

## Resume 1 (2026-11-07)

Relaunched `run_amend4_sessions.py` under the same freeze; done prefixes
skipped; halted slots are NOT re-run (recorded terminal rows). Continues at
eps_part2 RT of gpt-5.6-sol.
