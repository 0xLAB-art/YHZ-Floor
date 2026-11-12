# PREREGISTRATION — Amendment 4c: registered read-boundary repair (v5)

**Protocol:** PHASE2-EXTERNAL-ADMISSION-AMEND4C-BOUNDARY-REPAIR-v1 · **Namespace:** same · **Registered:** 2026-11-07, after the primary pass completed, BEFORE the repaired regrade was computed. Zero sessions, zero model calls (the Amend-2 pattern verbatim).

## 1. What the regrade exposed (disclosed motivation)

The Amendment-4 primary regrade under the frozen declared rule (v4) qualified
**5 of 57** retained programs; **52 rejections carry ONLY
`disallowed-boundary` violations (60 open calls, zero import violations)**.
The re-measured violating surface, by pattern:

| pattern | violating calls |
|---|---|
| variable bound to exactly one constant bare filename, `open(fn, "rb")` | 31 |
| literal filename, `open(name, "r", encoding=…)` | 18 |
| variable single-const binding, `open(fn, "r", encoding=…)` | 9 |
| variable bound to a non-constant expression | 2 |

Every one of these calls reads a declared in-sandbox artifact through the
working-directory contract the frozen prompts state; none changes access
authority. The v4 clause rejects them on syntax: it admits only
positional-argument opens of string-literal filenames (the Amend-2 branch)
and rejects keyword-carrying opens and variable-bound filenames outright —
while the Amendment-3 free-tier programs happened to write v4-shaped code
(`open("output.txt", "r")`, 261/282 qualified), the frontier programs write
the idiomatic `filename = "…"; open(filename, "r", encoding="ascii")` and
the clause rejects them all. This is the Amendment-1 lesson recurring with a
different syntactic surface: the rule's form, not the authority it guards.

## 2. The registered repair (v5)

One change to the boundary clause, applied to BOTH arms (declared v5 and
stress v5 — leaving it in one arm would confound the repair with the import
axis, the disclosed Amend-2 deviation's exact lesson). The clause admits a
read-only open of a bare in-sandbox filename that additionally carries ONLY
authority-preserving text-mode keyword parameters (encoding/errors/newline;
mode must remain read-only), and admits a filename variable **statically
bound to exactly ONE constant bare in-sandbox literal** (any reassignment,
expression binding, or non-bare literal keeps the rejection — conservative).
`**kwargs` are rejected. The sys.argv[1] branch keeps v4's exact strictness.
`build_v5_policies.py` generates both v5 modules from the frozen v4 modules
by this single diff; `V5_SANITY_CHECKS.json` records a 12-check battery
(qualified surfaces + rejected surfaces: write modes, traversal literals,
traversal-bound variables, re-assigned variables, expression bindings,
os/eval, `**kwargs`) — all PASS.

## 3. What is and is not claimed

- The **frozen-rule (v4) verdicts are quoted unchanged** as the registered
  primary product of Amendment 4 — including the quorum guard's outcome
  (programs on 2 of 7 tasks).
- The **v5 repaired regrade** recomputes per-program qualification and the
  per-label per-coding contrasts on the SAME frozen programs — zero sessions,
  zero model calls, deterministic.
- Both the pre-repair and repaired verdicts are printed side by side; the
  gap between them is the **boundary-clause owner's registered measurement**
  on external tasks.
- The residual 2 non-constant-bound violating calls stay rejected (the
  repair is conservative; the residual is disclosed per program).

## 4. Frozen inputs

`FREEZE_4C.json` hash-registers: this preregistration, `build_v5_policies.py`,
both generated v5 policy modules, `V5_SANITY_CHECKS.json`,
`run_amend4c_v5_regrade.py`, `regrade_amend4c_v5_contrast.py`, and the
primary `regrade_results_amend4.json` they consume. Committed before the
repaired regrade runs.
