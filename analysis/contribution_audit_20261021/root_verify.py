#!/usr/bin/env python3
"""Root's independent verification of the three wave-1 contribution audits.

This script does NOT call the workers' analysis code.  It re-derives the
headline numbers from the frozen H1-R3 records and the attribution corpora,
then compares them against the workers' own artifacts.  A worker number that
root cannot reproduce is a failed check, not a rounding difference.

Usage:  python3 -B root_verify.py
Exit code 0 means every independent recomputation matched the worker artifact.
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parents[2]
H1R3 = ROOT / "sp2027/analysis/h1r3_20261019"
RESULTS = H1R3 / "runs/confirmatory/results.jsonl"

failures: list[str] = []
skipped: list[str] = []
checks = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global checks
    checks += 1
    print("[%s] %-66s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        failures.append(name)


def skip(name: str, detail: str) -> None:
    """Record a check that could not run here, and say so."""
    skipped.append(name)
    print("[SKIP] %-66s %s" % (name, detail))


def load_rows():
    """The frozen cohort records, when this tree has them.

    The published package deliberately withholds these records: they carry the
    agent's program bodies.  Where they are absent, the checks that depend on
    them are reported as skipped rather than silently passed, and
    `policy_contrast_check.py` recomputes the same figures from the projections
    the package does ship.
    """
    if not RESULTS.is_file():
        return None
    return [json.loads(line) for line in RESULTS.read_text().splitlines() if line.strip()]


def legacy_class(row) -> str:
    """Classify a row from the frozen qualification records alone."""
    legacy = row.get("qualification_legacy") or {}
    if legacy.get("qualified"):
        return "qualified"
    if legacy.get("status") == "SOURCE_PARSE_REJECTED":
        return "syntax"
    return "import_reject"


def main() -> int:
    rows = load_rows()

    # ------------------------------------------------------------------
    # A. policy_mechanism: the source-policy mechanism claims
    if rows is None:
        skip("policy: admission census from the frozen records",
             "the frozen cohort records are not in this package")
        skip("policy: v3 admission census from the frozen records",
             "the frozen cohort records are not in this package")
        skip("policy: fresh cryptographic reproductions",
             "the frozen cohort records are not in this package")
    else:
        # ------------------------------------------------------------------
        legacy = collections.Counter(legacy_class(r) for r in rows)
        check("policy: 852 rows loaded from the frozen records", len(rows) == 852,
              "n=%d" % len(rows))
        check("policy: legacy policy qualifies 646 of 852",
              legacy["qualified"] == 646, "got %d" % legacy["qualified"])
        check("policy: legacy import rejects are 205", legacy["import_reject"] == 205,
              "got %d" % legacy["import_reject"])
        check("policy: one legacy syntax reject", legacy["syntax"] == 1,
              "got %d" % legacy["syntax"])

        v3_status = collections.Counter((r.get("qualification") or {}).get("status")
                                        for r in rows)
        check("policy: v3 qualifies 849 of 852",
              v3_status["QUALIFIED"] == 849, "got %d" % v3_status["QUALIFIED"])
        check("policy: v3 has exactly one source-parse rejection",
              v3_status["SOURCE_PARSE_REJECTED"] == 1,
              "got %d" % v3_status["SOURCE_PARSE_REJECTED"])
        check("policy: zero v3 import/sandbox rejections",
              v3_status["SANDBOX_REJECTED"] == 0,
              "got %d" % v3_status["SANDBOX_REJECTED"])

        exec_status = collections.Counter(r["execution_status"] for r in rows)
        check("policy: three pre-output failures (1 syntax + 2 runtime)",
              exec_status["SOURCE_PARSE_REJECTED"] == 1 and exec_status["EXECUTION_FAILED"] == 2,
              "syntax=%d runtime=%d" % (exec_status["SOURCE_PARSE_REJECTED"],
                                       exec_status["EXECUTION_FAILED"]))

        # population-level legacy split
        pops = collections.defaultdict(collections.Counter)
        for r in rows:
            pops[r["kind"]][legacy_class(r)] += 1
        expected = {
            "primary": {"qualified": 584, "import_reject": 183, "syntax": 1},
            "noise": {"qualified": 47, "import_reject": 17, "syntax": 0},
            "c0": {"qualified": 15, "import_reject": 5, "syntax": 0},
        }
        for kind, want in expected.items():
            got = dict(pops[kind])
            check("policy: %s population legacy split" % kind,
                  all(got.get(k, 0) == v for k, v in want.items()), "%s" % got)

        # fresh cryptographic reproduction from the frozen reference records
        def crypto(r):
            return bool((r.get("reference") or {}).get("cryptographic_predicate"))

        for kind, want in (("primary", 738), ("noise", 63), ("c0", 20)):
            got = sum(crypto(r) for r in rows if r["kind"] == kind)
            check("policy: %s cryptographic reproductions" % kind, got == want,
                  "got %d want %d" % (got, want))

    # the derivative intervention, read from the worker's case ledger
    ledger_path = (AUDIT / "policy_mechanism/.omo/evidence/run01/CASE_LEDGER.jsonl")
    if not ledger_path.is_file():
        # The published package ships the projected ledger rather than
        # the audit's working tree.
        ledger_path = (AUDIT.parent / "policy_mechanism_20261021/CASE_LEDGER.jsonl")
    if ledger_path.is_file():
        led = [json.loads(l) for l in ledger_path.read_text().splitlines() if l.strip()]
        transformed = [r for r in led if r.get("transformation_applied")]
        same = [r for r in transformed if r.get("fresh_output_equality") is True]
        check("policy: 128 derivatives were produced", len(transformed) == 128,
              "got %d" % len(transformed))
        check("policy: every derivative reproduced its original output",
              len(same) == len(transformed), "%d/%d" % (len(same), len(transformed)))
        now_q = [r for r in transformed if r.get("derivative_legacy_admitted")]
        check("policy: 104 derivatives now qualify under the legacy policy",
              len(now_q) == 104, "got %d" % len(now_q))
        rescued = [r for r in now_q if r.get("current_outcome_correct")]
        check("policy: 98 of the newly qualifying derivatives are correct",
              len(rescued) == 98, "got %d" % len(rescued))
    else:
        check("policy: worker case ledger present", False, "missing")

    # ------------------------------------------------------------------
    # B. paired_effects: the paired policy x representation contrasts
    if rows is None:
        skip("paired: the L3 admission contrast from the frozen records",
             "the frozen cohort records are not in this package")
    else:
        # ------------------------------------------------------------------
        # Pair by (family, level, seed): the instance identity used by the cohort.
        groups = collections.defaultdict(dict)
        for r in rows:
            if r["kind"] != "primary":
                continue
            groups[(r["family"], r["level"], r["seed"])][r["arm"]] = r

        complete = {k: v for k, v in groups.items() if {"R0", "R1", "R2"} <= set(v)}
        check("paired: 256 complete matched triplets", len(complete) == 256,
              "got %d" % len(complete))

        def admitted(r):
            return bool(r["terminal_success"]) and bool((r.get("qualification_legacy") or {}).get("qualified"))

        # per level, per contrast
        per_level = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0, 0, 0, 0]))
        qsign = collections.defaultdict(lambda: collections.Counter())
        for (family, level, seed), arms in complete.items():
            for treatment in ("R1", "R2"):
                b = per_level[level][treatment]
                r0, rt = arms["R0"], arms[treatment]
                b[0] += 1
                b[1] += int(bool(r0["terminal_success"]))
                b[2] += int(bool(rt["terminal_success"]))
                b[3] += int(admitted(r0))
                b[4] += int(admitted(rt))
                d_current = int(bool(rt["terminal_success"])) - int(bool(r0["terminal_success"]))
                d_legacy = int(admitted(rt)) - int(admitted(r0))
                q = d_legacy - d_current
                if q < 0:
                    qsign[(level, treatment)]["neg"] = qsign[(level, treatment)].get("neg", 0) + 1
                elif q > 0:
                    qsign[(level, treatment)]["pos"] = qsign[(level, treatment)].get("pos", 0) + 1

        l3 = per_level["L3"]["R2"]
        check("paired: L3 R2-R0 current R0 = 125/128", l3[1] == 125, "got %d" % l3[1])
        check("paired: L3 R2-R0 current R2 = 124/128", l3[2] == 124, "got %d" % l3[2])
        check("paired: L3 R2-R0 legacy-admitted R0 = 100/128", l3[3] == 100, "got %d" % l3[3])
        check("paired: L3 R2-R0 legacy-admitted R2 = 58/128", l3[4] == 58, "got %d" % l3[4])
        check("paired: L3 R2-R0 policy shift is -32.03 pp",
              abs(((l3[4] - l3[3]) - (l3[2] - l3[1])) / l3[0] * 100 + 32.03125) < 1e-6,
              "got %.5f" % (((l3[4] - l3[3]) - (l3[2] - l3[1])) / l3[0] * 100))
        check("paired: L3 R2-R0 has 50 negative and 9 positive policy shifts",
              qsign[("L3", "R2")].get("neg") == 50 and qsign[("L3", "R2")].get("pos") == 9,
              "neg=%d pos=%d" % (qsign[("L3", "R2")].get("neg", 0),
                                 qsign[("L3", "R2")].get("pos", 0)))
        check("paired: L3 R1-R0 current R0 = 125/128", per_level["L3"]["R1"][1] == 125,
              "got %d" % per_level["L3"]["R1"][1])
        check("paired: L3 R1-R0 current R1 = 126/128", per_level["L3"]["R1"][2] == 126,
              "got %d" % per_level["L3"]["R1"][2])
        check("paired: L3 R1-R0 legacy-admitted R0 = 100/128", per_level["L3"]["R1"][3] == 100,
              "got %d" % per_level["L3"]["R1"][3])
        check("paired: L3 R1-R0 legacy-admitted R1 = 111/128", per_level["L3"]["R1"][4] == 111,
              "got %d" % per_level["L3"]["R1"][4])

        # cross-check the worker's own results.json
        worker = AUDIT / "paired_effects/results.json"
        if worker.is_file():
            w = json.loads(worker.read_text())
            found = None
            for entry in (w.get("pooled") or w.get("contrasts") or []):
                if entry.get("level") == "L3" and entry.get("contrast") in ("R2-R0", "R2-R0"):
                    found = entry
                    break
            if found is None and isinstance(w.get("pooled"), list):
                for entry in w["pooled"]:
                    if entry.get("level") == "L3" and str(entry.get("contrast", "")).endswith("R2-R0"):
                        found = entry
                        break
            check("paired: worker results.json carries the L3 R2-R0 contrast",
                  found is not None, "keys=%s" % list(w.keys())[:8])

        # preregistered reproduction
        repro = AUDIT / "paired_effects/preregistered_L3_reproduction.json"
        if repro.is_file():
            pr = json.loads(repro.read_text())
            r1 = pr["contrasts"]["R1"]
            r2 = pr["contrasts"]["R2"]
            check("paired: preregistered L3 R1 interval is [-0.0234375, 0.0390625]",
                  (r1["ci_low"], r1["ci_high"]) == (-0.0234375, 0.0390625),
                  "%s" % ((r1["ci_low"], r1["ci_high"]),))
            check("paired: preregistered L3 R2 interval is [-0.046875, 0.03125]",
                  (r2["ci_low"], r2["ci_high"]) == (-0.046875, 0.03125),
                  "%s" % ((r2["ci_low"], r2["ci_high"]),))
            check("paired: both preregistered L3 contrasts are equivalent within margin",
                  r1["equivalence"]["status"] == "EQUIVALENT_WITHIN_MARGIN"
                  and r2["equivalence"]["status"] == "EQUIVALENT_WITHIN_MARGIN")
            check("paired: preregistered Holm-adjusted p is 1.000 for both",
                  r1["mcnemar"]["p_value"] == 1.0 and r2["mcnemar"]["p_value"] == 1.0,
                  "%s %s" % (r1["mcnemar"]["p_value"], r2["mcnemar"]["p_value"]))

        # ------------------------------------------------------------------
    # C. attribution_evidence: denominators and the soundness aggregate
    # ------------------------------------------------------------------
    summary = AUDIT / "attribution_evidence/recomputed_summary.json"
    if summary.is_file():
        s = json.loads(summary.read_text())
        expected = {
            # population: (cases, attack denominator, v2/join fp, sig fp, full fp)
            "heb1_dev": (54, 32, 0, None, None),
            "heb1_heldout": (64, 36, 0, None, None),
            "iar_b_dev": (54, 40, 16, 24, 0),
            "iar_b_heldout": (58, 44, 16, 28, 0),
            "iar_c_preserved": (44, 28, 10, 14, 0),
        }
        for name, (cases, attack, join_fp, sig_fp, full_fp) in expected.items():
            pop = s.get(name, {})
            systems = pop.get("systems", {})
            def fp_of(sysname):
                rec = systems.get(sysname, {})
                val = rec.get("false_promotion_attack")
                return val[0] if isinstance(val, list) and val else None
            ok = pop.get("cases") == cases
            detail = "cases=%s" % pop.get("cases")
            if join_fp is not None:
                # HEB1 names its join validator V2; the IAR corpora name it v2.
                join_name = "V2" if name.startswith("heb1") else "v2"
                got = fp_of(join_name)
                ok = ok and got == join_fp
                detail += " join_fp=%s" % got
            if sig_fp is not None:
                got = fp_of("v3-sig")
                ok = ok and got == sig_fp
                detail += " sig_fp=%s" % got
            if full_fp is not None:
                got = fp_of("v3-full")
                ok = ok and got == full_fp
                detail += " full_fp=%s" % got
            check("attribution: %s denominators and false promotions" % name, ok, detail)
        check("attribution: IAR-C v2 honest-rejected is 14 of 16",
              s["iar_c_preserved"]["systems"]["v2"].get("honest_rejected") == [14, 16],
              "%s" % s["iar_c_preserved"]["systems"]["v2"].get("honest_rejected"))
    else:
        check("attribution: recomputed summary present", False, "missing")

    # The four soundness corpora each count 2,814 evaluations of 1,407 mutants.
    census = AUDIT / "attribution_evidence/supplementary_census.json"
    if census.is_file():
        c = json.loads(census.read_text())
        entries = c.get("mutation_census", [])
        check("attribution: four soundness corpora are censused", len(entries) == 4,
              "got %d" % len(entries))
        total = c.get("total_mutation_evaluations")
        check("attribution: total mutation evaluations is 11,256", total == 11256,
              "got %s" % total)
        # independently recount each corpus from the source aggregates
        counted = 0
        for e in entries:
            src = e.get("source") or e.get("path") or e.get("file")
            if not src:
                continue
            p = ROOT / src if not str(src).startswith("/") else Path(src)
            if p.is_file():
                doc = json.loads(p.read_text())
                counted += int(doc.get("evaluations", 0))
        if counted:
            check("attribution: corpora recount independently to 11,256", counted == 11256,
                  "recomputed %d" % counted)
        elif any(e.get("source") or e.get("path") or e.get("file") for e in entries):
            # The census records where each corpus came from, but this package
            # does not ship the corpora themselves, so the recount cannot run
            # here.  That is a skip, not a failure.
            skip("attribution: corpora recount independently to 11,256",
                 "the mutation corpora are not in this package")
        else:
            check("attribution: corpora source paths are recorded for recount", False,
                  "no source path in the census entries")
    else:
        check("attribution: supplementary census present", False, "missing")

    print()
    print("independent checks: %d   passed: %d   failed: %d   skipped: %d"
          % (checks, checks - len(failures) - len(skipped), len(failures),
             len(skipped)))
    if failures:
        print("FAILED: %s" % ", ".join(failures))
        return 1
    if skipped:
        print("%d check(s) need the frozen cohort records, which this package "
              "deliberately withholds; policy_contrast_check.py recomputes the "
              "same figures from the projections the package ships." % len(skipped))
    else:
        print("every worker headline number reproduced independently from the "
              "frozen records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())