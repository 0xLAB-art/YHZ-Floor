# REFERENCE SOLVER — explicit empty state

`reference_solve_run.jsonl` contains **zero records**. This is not a missing
artifact: the offline stdlib-only reference-solve step exists in the mirrored
Phase-2 protocol to *prove exact answer reproduction for qualifying tasks*
(`selection/reference_solvers/solve_<task>.py` compared against pinned metadata
answers). In this phase the qualifying set is **empty** — 0 of 40 pinned
CVE-Bench tasks qualify (see `TASK_SELECTION.md`, `census.json`):

- No static deterministic answer string exists to reproduce (native scoring is
  a server-side exploit probe, `src/cvebench/cvebench.py:82`).
- The protected goal object (secret file/table) exists only inside the running
  service, so there is nothing an offline solver could compute or verify.

Writing a solver with nothing to solve would be fabrication, so none was
written. The `selection/reference_solvers/` directory is empty for the same
reason. This mirrors the Phase-2 handling of `sessions/` and `regrade/` on its
own early stop.
