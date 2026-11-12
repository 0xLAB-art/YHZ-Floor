# Route

All ten sessions of arm `C_NO_ORACLE` executed on a single route:

| Endpoint | Model | Sessions |
|---|---|---|
| `https://api.apinex.bond/v1/chat/completions` | `free/deepseek-v4.1-flash` | 10/10 |

Prompt bytes, policy, predicate, oracle budget and the frozen runner are byte-identical
to `PREREGISTRATION.md`. The only substitution relative to the H2 cohort is the model
name, recorded here and in `FREEZE.json`; that substitution is what makes this a
single-arm separation control rather than a matched A/B control.

Provider-side connection failures are infrastructure events, not observations: they
produced no session, no submission and no oracle call, and are therefore not recorded
as results of this arm. APINEX is the standing route for this line of work.
