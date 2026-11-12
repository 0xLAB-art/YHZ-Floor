# sessions/ — EMPTY STATE

**Zero experiment sessions were run in this phase.**

The phase stopped at task selection with status `no_go`: 4 of the required 6
crypto tasks qualified from the pinned Cybench archive
(`../selection/census.json`, `../TASK_SELECTION.md`). The session grid
(6 tasks × {R0, RT} × seeds 71, 72 = 24 sessions) was therefore never
instantiated, and no model call was ever made beyond the non-evidence
AUTH_SMOKE probe (`../HEALTH.json`).

Consequently there are no terminal states, no retained failures, no raw
provider responses, and no transcripts. Terminal-state enum discipline and
no-retry rules had nothing to apply to.

The exact prompts the frozen design would have sent are recorded with hashes in
`../PROMPT_HASHES.json` and reproducible from the frozen
`../fixtures/rt_transform/build_representations.py` + frozen fixtures.
