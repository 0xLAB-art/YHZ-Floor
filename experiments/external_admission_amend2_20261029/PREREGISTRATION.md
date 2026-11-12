# PREREGISTRATION — Amendment 2: read-only in-sandbox instance access under rule (a)

**Protocol:** `PHASE2-EXTERNAL-ADMISSION-v1` + **AMENDMENT2**
**Namespace:** `sp2027/research_execution/external_admission_amend2_20261029/`
**Date written:** 2026-10-29 (UTC)
**Base freeze:** `external_admission_amend1_20261024` (37 programs, frozen 2026-10-24)
**Model calls under this amendment:** zero. **New sessions:** zero.
**Status:** amendment proposed after a post-freeze observation; declared post-hoc.

---

## 1. Motivating observation (recorded before the amendment)

In `external_admission_amend1_20261024/regrade/regrade_results_amend1.json`:

- rule (a) admitted **0/37** and rule (b) admitted **0/37** → movement 0.0 pp on all four tasks.
- The degeneracy diagnostic attributes the rejection to one clause: `open:not-readonly-argv1`
  (37/37 programs carry at least one such violation).
- Re-reading the 37 retained sources: **every program contains exactly one `open` call, and it is
  `open('output.txt', 'r')`** — 37/37, no path separators, no traversal, no write mode, no
  exception.
- 31/37 programs have **no other** rule-(a) violation. The remaining 6 additionally import
  `Crypto.PublicKey` / `Crypto.Cipher` (pycryptodome), which rule (a) never allowed.

Interpretation: the v3 clause was ported from an internal harness whose executor receives the
instance path in `argv[1]`. The external sandbox instead materialises the instance as
`output.txt` in the working directory. The clause therefore rejected programs for the *shape of
the interface*, not for any authority they exercised.

## 2. The amendment (one predicate)

`policies/rule_a_permissive_v4.py`, `_is_allowed_instance_read` gains one branch:

```python
if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
    name = arg.value
    if not name or "/" in name or "\\" in name or name in (".", ".."):
        return False                      # bare in-sandbox filename only
    if len(node.args) == 1:
        return True
    mode = node.args[1]
    return isinstance(mode, ast.Constant) and mode.value in {"r", "rt", "rb"}
```

Unchanged: the allowed-module set, forbidden modules, forbidden calls, forbidden substrings,
`POLICIES`, `qualify_source`, rule (b), rule (c), the 37 programs, their oracle labels, and every
session record. `qualify_source` is byte-identical between v3 and v4 (verified with `diff`).

## 3. Estimand and decision rule

For each frozen program: `admitted = qualified(rule) AND oracle_match`, where `oracle_match` is the
label recorded at session time (a frozen input, not re-executed).

Per task: `contrast_rule_pp = 100 * admitted_rule / n`, `movement = contrast_b − contrast_a`.
Margin ±10 pp, as in amend1.

Falsifiers (unchanged from amend1):

- **F1 (mechanism ports to the external boundary):** movement outside ±10 pp on **≥2 of 4** tasks.
- **F2 (honest null):** movement within ±10 pp on **≥3 of 4** tasks.

## 4. Prediction (recorded before running the regrade)

31/37 qualify under (a) v4; 19/37 are admitted; movement = **−100.0 / −33.3 / 0.0 / −77.8 pp**
(Dynastic / Makeshift / Partial Tenacity / Primary Knowledge); **F1 TRUE**, **F2 FALSE**;
Partial Tenacity stays 0/8 because of the pycryptodome imports.

## 5. Gates

1. Every program's sha256 equals the value recorded in the frozen amend1 regrade.
2. Rule v3 reproduces the frozen rule-(a) decision (qualified flag and violation count) for every
   program.
Any gate failure aborts the run with a non-zero exit; no output is written.

## 6. What this does and does not establish

**Establishes:** the admission contrast of rule (a) versus rule (b) is measurable *outside the
authors' own harness*, on 37 retained external programs, once the interface defect is repaired.

**Does not establish:** a new capability rate; a fourth-task result; that the amendment was
pre-specified (it was not); or that rule (a) is the "correct" policy. Rule (a) remains a declared
permissive rule and rule (b) a deliberate stress counterfactual.

**Disclosed limitations:** post-hoc amendment; no re-execution; rule (c) not evaluable because
rule (b) admits 0/37; pycryptodome exclusion left in place; oracle labels are the session-time
record.

---

## 7. Post-outcome addendum (2026-10-29, written after the regrade)

This section is added **after** the outcome and is not part of the frozen prediction above.

Section 3 of this document defines `contrast_rule_pp` as an **admission rate** and applies the
designation F1 to its movement. The parent protocol
(`external_admission_20261024/PREREGISTRATION.md`, §7) defines F1 on the **per-task
representation contrast** (R0 minus RT), which is a different quantity. The prediction above is
retained unmodified as the record of what was anticipated; the correction is recorded here.

Recomputation of the parent quantity from frozen inputs (`regrade_amend2_contrast.py` →
`regrade_contrast_amend2.json`), with the interface repair applied to **both** arms (a post-outcome
deviation: leaving rule (b) unrepaired confounds the repair with the import filter):

- the declared arm qualifies **31/37** and **19/19** oracle-correct programs; the stress arm
  qualifies **20/37** and retains only **12/19** correct programs, discarding all seven Primary
  Knowledge ones;
- the regraded representation contrast is therefore **undefined on 2 of 4 tasks** (Primary
  Knowledge, Partial Tenacity) and **identical between rules** on the other two (0.0 and −100.0 pp);
  movement is 0.0 pp where defined, and **F1 is FALSE** (0 of 4 moved; threshold 2). F2 holds
  vacuously;
- the admission-rate contrast predicted in §4 (−100.0 / −33.3 / 0.0 / −77.8 pp) is an artifact of
  comparing a repaired arm against the unrepaired rule (b); it is **withdrawn** as a headline and
  replaced by the narrower, supported statement: the stricter rule discards **7 of 19** correct
  programs.

Consequence for the manuscript: the amendment is reported as making the **declared** arm
non-degenerate and the external boundary an **evaluator-sensitivity** result; no portability claim
is upgraded, and both the earlier "F1 TRUE" reading and the "1 of 4 tasks moved" reading are
withdrawn.
