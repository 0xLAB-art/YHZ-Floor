# H2-CBC-NOORACLE-20261103-v1 — registered matched oracle-separation ablation

**Status:** registered before the first provider call. Frozen hashes are written
to `FREEZE.json` by the runner *before* the first call; no session is retried.

## Why this arm exists

The H2 wrapper cohort (frozen seeds 61–64, extension seeds 65–74) contrasts two
session shapes, but **both arms had oracle access**: every recorded session in
`h2_pairs_extension_20261024` shows `oracle_usage_present=true`. So the cohort
cannot separate *session shape* from *oracle-information channel*, and nothing
in the repository measures what happens when the channel is present but carries
no information. This arm closes that gap for one task family.

Scope note, stated here so it cannot be upgraded later: this is a **matched
oracle-separation ablation on the CBC task**, not an E5 acquisition result. It
tests the contract's information-dependence claim on a single controlled
stressor; it does not touch the acquisition architecture, which remains
unresolved and is reported as such.

## Design (matched to `H2-CBC-PAIRS-EXT-20261024-v1`)

| Factor | Matched value |
|---|---|
| Seeds | exactly 65, 66, 67, 68, 69, 70, 71, 72, 73, 74 (same `fixture_cbc.instance`) |
| Prompt | the frozen `PROMPT_TEMPLATE`, unmodified (byte-identical to arm B's turn-1 prompt) |
| Model / route | `APMIX_MODEL` from the operator `.env` (same route as the extension cohort) |
| `max_tokens` | 3000, unchanged |
| Turns | 1, no feedback (one-shot, as arm B) |
| Execution | frozen `run_program`: interpreter + `agent.py` + `public.json`, `shell=False`, scrubbed env, 20 s |
| Policy | frozen `policy_check` (imports json/sys/hashlib/cryptography/oracle; no eval/exec) |
| Predicate | frozen `verdict`: exact match on `plaintext_hex`, lowercased |
| Oracle budget | 4096 calls, unchanged |

**The single manipulated factor is the oracle's information content.**

`oracle.query(block_hex)` keeps its interface and its budget but **always returns
`False`**, and every call is counted. Interface-present / information-absent is
deliberate: a program written for the oracle then runs to completion and fails
on the merit of having learned nothing, instead of dying on `ImportError`. That
separates "no information" from "no module", which a removed module would
conflate.

Why this is a valid separation for this task: the CBC padding attack's only
non-public signal is the validity bit. An oracle that never reports valid
padding leaves the plaintext unrecoverable from the public fields by that route,
so acceptance under this arm cannot be attributed to the oracle channel.

## Endpoints, fixed before the run

- **Primary:** accepted sessions / 10, frozen predicate, no tolerance.
- **Secondary:** oracle attempts per session (does the program even try the
  channel?), submissions, non-submission reasons, execution stages, and, for
  any acceptance, the **non-oracle route** that explains it (recorded verbatim
  from the recovered program).
- **Descriptive only:** comparison against A (5/10 registered) and B (7/10
  registered) from the extension cohort. No pooling, no combined inference, no
  new Fisher claim over these three arms.

## Predictions (before data)

- **H_null:** acceptance 0/10, with oracle attempts ≥ 1 on most seeds — programs
  use the channel and learn nothing from it. This is the outcome that supports
  the information-dependence claim.
- **H_alt:** any acceptance. Then a non-oracle path exists on this task
  (recovered plaintext from public fields, known-plaintext structure, or a
  computation error in the fixture), and the information-dependence claim for
  this task weakens. Each acceptance is inspected individually and reported
  whether or not it is convenient.

## Falsifiers

- **F-C1:** acceptance > 0 that cannot be explained by a recorded non-oracle
  route → the contract's information-dependence claim is challenged on this
  task. Reported as a failure of the claim, not re-adjudicated away.
- **F-C2:** zero submissions (all 10 fail at parse/policy) → the arm measures
  output-contract compliance, not information dependence; reported as such, and
  the parse-failure diagnosis of 2026-11-03 applies.
- **F-C3:** provider availability < 10/10 evaluable → recursive-fraction
  reporting only; H_null is not claimed at full strength.

## Disclosure

`results.jsonl`, raw provider bodies, prompts, and execution captures are kept
verbatim. Provider calls are logged per call in `../BUDGET_LEDGER.jsonl` with
the route's reported free-plan status. If a call fails, it is recorded as a
provider failure and never retried.
