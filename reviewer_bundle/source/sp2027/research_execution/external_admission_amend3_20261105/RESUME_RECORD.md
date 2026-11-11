# Amendment 3 — execution halt and resume record (pre-outcome)

- **Halt:** 2026-11-05, after **47/168** sessions (all `free/gpt-6-luna`), the
  runner stopped `halted` on the registered rule (>=3 consecutive
  provider-side pre-output failures). The three affected slots are
  `2018q-cry-lowe` / `RT` / seeds 417, 418, 419; each exhausted its 3 immediate
  attempts with **HTTP 429 (rate limit)** and produced no model content.
- **No task-side terminal state:** the three slots are `PROVIDER_UNAVAILABLE`
  with `produced_model_content=false`; per §8 they are excluded from
  acceptance denominators exactly because no model content was produced.
- **Provider recovery:** 16-token non-evidence probes for all three labels
  (`free/gpt-6-luna`, `free/qwen-3.8-max`, `free/deepseek-v4.1-flash`)
  returned ok with `cost_tokens=0`.
- **Resume:** the same frozen design, prompts, policies, oracle, and F1 script;
  the runner skips the recorded prefixes and runs the remaining **121** slots
  (168 total minus 47 recorded; the three 429 slots remain excluded). No
  criterion, prompt, policy, or analysis change.
- **Disclosure:** the final REPORT will record this halt/resume and the three
  excluded slots. The halt is an infrastructure event, not a task-side
  outcome and not a benchmark claim.

This record is written before the resumed execution; it is an operational
record, not an outcome analysis.

## Second halt (after resume 1)

- **Halt:** 2026-11-05, after **108/168** sessions (`free/gpt-6-luna` 56/56;
  `free/qwen-3.8-max` 52/56). The runner halted on the same pre-registered
  >=3-consecutive rule. Five qwen slots were recorded `PROVIDER_UNAVAILABLE`
  with `produced_model_content=false`: `2018q-cry-babycrypto` / R0 / seeds
  419, 420; `2021q-cry-crack_me` / R0 / seeds 418, 419, 420. All exhausted
  their 3 immediate attempts on **HTTP 429**.
- **Total exclusions after two halts:** 8 slots (3 gpt-6-luna + 5 qwen), all
  provider_no_content, excluded from acceptance denominators per §8.
- **Provider recovery:** 16-token probes for all three labels returned ok,
  `cost_tokens=0`.
- **Resume (2):** same frozen design and inputs; the runner skips recorded
  prefixes and runs the remaining **60** slots — qwen `crack_me` / RT / seeds
  417-420 (4) and the full `free/deepseek-v4.1-flash` label (56). No criterion,
  prompt, policy, or analysis change.

## Third halt (after resume 2)

- **Halt:** 2026-11-05, after **123/168** sessions (`free/gpt-6-luna` 56/56;
  `free/qwen-3.8-max` 56/56; `free/deepseek-v4.1-flash` 11/56). Three
  deepseek slots were recorded `PROVIDER_UNAVAILABLE` with no model content:
  `2015q-cry-eps_part2` / R0 / seeds 417, 418, 419, all on HTTP 429 after
  three immediate attempts.
- **Total exclusions after three halts:** 11 slots (3 gpt-6-luna, 5 qwen,
  3 deepseek), all provider_no_content; excluded from acceptance denominators
  per §8. The remaining unattempted slots: **45 deepseek**.
- **Operational response:** record halt; build and test the offline regrade
  harness on the 123 completed sessions while the free-tier quota recovers;
  then resume the remaining deepseek slots under the same frozen design.

## Final completion (after resume 3)

- The runner completed **168/168** sessions (`halted=false`), accounting cost
  $0.00. Execution windows: 47 + 61 + 15 + 45 sessions (four windows; three
  halts on HTTP 429 and three resumes).
- **12 slots excluded** as `PROVIDER_UNAVAILABLE` with
  `produced_model_content=false`, all on HTTP 429: 3 gpt-6-luna (lowe/RT
  417-419), 5 qwen (babycrypto/R0 419-420; crack_me/R0 418-420), 4 deepseek
  (eps_part2/R0 417-419; lowe/RT 419). Per §8 they are excluded from
  acceptance denominators exactly because they produced no model content.
- **156 sessions produced content; 282 programs retained; 0 oracle-correct.**
- The registered grid is complete; the offline triple regrade and the per-label
  F1/F2/F3 analysis now run on all retained programs.
