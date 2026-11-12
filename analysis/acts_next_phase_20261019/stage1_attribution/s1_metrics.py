#!/usr/bin/env python3
"""Post-hoc metric computation for TOEEA-1.

**This script is NOT part of the frozen measurement code.**  It was written
after the confirmatory run, it performs no measurement, and it reads only
``runs/results.json`` (the raw per-case outcomes) and
``s1_case_manifest.json`` (the frozen case table).  Every number it prints is
a recomputation over the frozen raw results.

It reports three metric sets:

  SET 1  the metric exactly as preregistered in ``s1_protocol.md`` section 5,
         computed against the preregistered ``crypto_success`` ground truth.
         Reported for completeness, with the caveat in section 5.1.

  SET 2  the same four quantities computed against the **attribution ground
         truth**: a bundle is a success iff the frozen case table says its
         expected decision is ``ATTRIBUTED_SUCCESS``.  This is the metric that
         answers the research question.  Added post-hoc; see
         ``s1_deviations.md`` D-06.

  SET 3  decomposed by family: honest-execution confusion (family A),
         contradiction-detection rate (families C and R), and
         omission-classification rate (family B), plus the frozen Stage01
         pair's own table.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

STAGE1_ROOT = Path(__file__).resolve().parent
RESULTS = STAGE1_ROOT / "runs" / "results.json"
MANIFEST = STAGE1_ROOT / "s1_case_manifest.json"
OUT_MD = STAGE1_ROOT / "runs" / "summary.md"
OUT_JSON = STAGE1_ROOT / "runs" / "summary.json"

EVALUATORS = ("digest_only", "signed_digest_only", "signed_context_only",
              "full", "full_lenient")
SUCCESS = "ATTRIBUTED_SUCCESS"
REJECT = "REJECT"
INCONCLUSIVE = "INCONCLUSIVE"


def wilson(successes: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (None, None)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom)
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def ci(successes: int, n: int) -> str:
    lo, hi = wilson(successes, n)
    if lo is None:
        return "n/a"
    return f"[{lo:.3f},{hi:.3f}]"


def main() -> int:
    raw = json.loads(RESULTS.read_text())
    results = raw["results"]
    manifest = json.loads(MANIFEST.read_text())
    expected_by_id = {c["case_id"]: c for c in manifest["cases"]}

    def decision(rec, evaluator):
        return rec["decisions_detail"][evaluator]["decision"]

    lines: list[str] = []
    out: dict = {"schema": "acts-next-phase/s1-summary/1", "case_count": len(results)}

    lines.append("# TOEEA-1 — Confirmatory results (recomputed from frozen raw results)")
    lines.append("")
    lines.append(f"* Cases: **{len(results)}** (frozen table: {manifest['case_count']})")
    lines.append(f"* Raw results: `runs/results.json` (schema `{raw['schema']}`)")
    lines.append("* Computed by `s1_metrics.py` (post-hoc recomputation; no measurement)")
    lines.append("")

    # ------------------------------------------------------------------
    # SET 1 -- preregistered metric (crypto_success ground truth)
    # ------------------------------------------------------------------
    lines.append("## SET 1 — preregistered metric (`s1_protocol.md` §5), ground truth = `crypto_success`")
    lines.append("")
    n_crypto_true = sum(1 for r in results if expected_by_id[r["case_id"]]["expected_crypto_success"] is True)
    n_crypto_false = len(results) - n_crypto_true
    lines.append(f"Denominators: `crypto_success == true` **n={n_crypto_true}**, "
                 f"`crypto_success == false` **n={n_crypto_false}** "
                 f"(the protocol's illustrative 14/13 did not match the frozen manifest; "
                 f"the protocol fixes the *rule*, the manifest fixes the numbers).")
    lines.append("")
    set1 = {}
    for ev in EVALUATORS:
        fa = [r["case_id"] for r in results
              if expected_by_id[r["case_id"]]["expected_crypto_success"] is False
              and decision(r, ev) == SUCCESS]
        fr = [r["case_id"] for r in results
              if expected_by_id[r["case_id"]]["expected_crypto_success"] is True
              and decision(r, ev) in (REJECT, INCONCLUSIVE)]
        ca = [r["case_id"] for r in results
              if expected_by_id[r["case_id"]]["expected_crypto_success"] is True
              and decision(r, ev) == SUCCESS]
        cr = [r["case_id"] for r in results
              if expected_by_id[r["case_id"]]["expected_crypto_success"] is False
              and decision(r, ev) in (REJECT, INCONCLUSIVE)]
        set1[ev] = {"false_attribution": fa, "false_rejection": fr,
                     "correct_attribution": ca, "correct_rejection": cr}
        lines.append(f"* **{ev}** — FA {len(fa)}/{n_crypto_false} {ci(len(fa), n_crypto_false)}"
                     f" · FR {len(fr)}/{n_crypto_true} {ci(len(fr), n_crypto_true)}"
                     f" · CA {len(ca)}/{n_crypto_true} · CR {len(cr)}/{n_crypto_false}")
    lines.append("")
    lines.append("### §5.1 caveat (material)")
    lines.append("")
    lines.append("The preregistered `crypto_success` field records **whether the cryptographic "
                 "predicate is true on the presented output**. For the C family the predicate is "
                 "true by construction (the contradiction is *elsewhere*: the credited program was "
                 "not the executed one, the output was not observed, the signature was tampered, "
                 "and so on), while the correct decision for those cases is REJECT. The FR and CR "
                 "columns above therefore count E3's **correct** rejections of the C family as "
                 "'false rejections'. SET 1 is reported because it is the preregistered metric; "
                 "**SET 2 is the interpretable one** and is a post-hoc addition (deviation D-06).")
    lines.append("")

    # ------------------------------------------------------------------
    # SET 2 -- attribution ground truth
    # ------------------------------------------------------------------
    lines.append("## SET 2 — attribution ground truth (a bundle is a success iff the frozen")
    lines.append("case table says its expected decision is `ATTRIBUTED_SUCCESS`)")
    lines.append("")
    truth_success = [r["case_id"] for r in results
                     if expected_by_id[r["case_id"]]["expected_decision"] == SUCCESS]
    truth_failure = [r["case_id"] for r in results
                     if expected_by_id[r["case_id"]]["expected_decision"] != SUCCESS]
    n_s, n_f = len(truth_success), len(truth_failure)
    lines.append(f"Denominators: ground-truth success **n={n_s}** "
                 f"({', '.join(truth_success)}), ground-truth non-success **n={n_f}**.")
    lines.append("")
    lines.append("| contract | false attribution | Wilson 95% | correct attribution | false rejection | Wilson 95% | correct rejection |")
    lines.append("|---|---|---|---|---|---|---|")
    set2 = {}
    for ev in EVALUATORS:
        fa = [r["case_id"] for r in results
              if r["case_id"] in truth_failure and decision(r, ev) == SUCCESS]
        ca = [r["case_id"] for r in results
              if r["case_id"] in truth_success and decision(r, ev) == SUCCESS]
        fr = [r["case_id"] for r in results
              if r["case_id"] in truth_success and decision(r, ev) in (REJECT, INCONCLUSIVE)]
        cr = [r["case_id"] for r in results
              if r["case_id"] in truth_failure and decision(r, ev) in (REJECT, INCONCLUSIVE)]
        set2[ev] = {"false_attribution": fa, "correct_attribution": ca,
                    "false_rejection": fr, "correct_rejection": cr,
                    "fa_rate": [len(fa), n_f], "fr_rate": [len(fr), n_s]}
        lines.append(f"| `{ev}` | **{len(fa)}/{n_f}** | {ci(len(fa), n_f)} | {len(ca)}/{n_s} | "
                     f"**{len(fr)}/{n_s}** | {ci(len(fr), n_s)} | {len(cr)}/{n_f} |")
    lines.append("")
    for ev in EVALUATORS:
        fa = set2[ev]["false_attribution"]
        if fa:
            lines.append(f"* `{ev}` false attributions: {', '.join(f'`{x}`' for x in fa)}")
    lines.append("")

    # ------------------------------------------------------------------
    # SET 3 -- family decomposition
    # ------------------------------------------------------------------
    lines.append("## SET 3 — family decomposition")
    lines.append("")
    fam_a = [r["case_id"] for r in results if r["family"] == "A"]
    fam_b = [r["case_id"] for r in results if r["family"] == "B"]
    fam_c = [r["case_id"] for r in results if r["family"] in ("C", "R")]
    lines.append(f"Family A (honest executions) n={len(fam_a)}; family B (omission) n={len(fam_b)}; "
                 f"families C+R (contradiction + replay) n={len(fam_c)}.")
    lines.append("")
    lines.append("| contract | A: success attributed | A: non-success not promoted | B: INCONCLUSIVE | B: REJECT | C+R: detected (REJECT) |")
    lines.append("|---|---|---|---|---|---|")
    set3 = {}
    for ev in EVALUATORS:
        def d(cid):
            rec = next(r for r in results if r["case_id"] == cid)
            return decision(rec, ev)
        a_ok = sum(1 for c in fam_a if expected_by_id[c]["expected_decision"] == SUCCESS and d(c) == SUCCESS)
        a_tot = sum(1 for c in fam_a if expected_by_id[c]["expected_decision"] == SUCCESS)
        a_bad = sum(1 for c in fam_a if expected_by_id[c]["expected_decision"] != SUCCESS and d(c) == SUCCESS)
        b_inc = sum(1 for c in fam_b if d(c) == INCONCLUSIVE)
        b_rej = sum(1 for c in fam_b if d(c) == REJECT)
        c_det = sum(1 for c in fam_c if d(c) == REJECT)
        set3[ev] = {"a_success_attributed": [a_ok, a_tot], "a_non_success_promoted": a_bad,
                    "b_inconclusive": [b_inc, len(fam_b)], "b_reject": b_rej,
                    "cr_detected": [c_det, len(fam_c)]}
        lines.append(f"| `{ev}` | {a_ok}/{a_tot} | {a_bad} promoted | {b_inc}/{len(fam_b)} | "
                     f"{b_rej}/{len(fam_b)} | **{c_det}/{len(fam_c)}** |")
    lines.append("")

    # -- frozen Stage01 pair -------------------------------------------
    lines.append("### Frozen Stage01 pair (real frozen components, not a model)")
    lines.append("")
    applicable = [r for r in results if r["stage01"].get("applicable")]
    accepted = [r["case_id"] for r in applicable
                if r["stage01"].get("stage01_final_decision") == "ACCEPTED"]
    lines.append(f"Cases with a direct Stage01 analogue: **{len(applicable)}/{len(results)}**; "
                 f"the other {len(results) - len(applicable)} are **N/A** (no analogue exists) "
                 f"and are not counted in either direction.")
    lines.append("")
    lines.append("| case | Stage01 final | E3 (`full`) | ground truth |")
    lines.append("|---|---|---|---|")
    for r in applicable:
        cid = r["case_id"]
        gt = expected_by_id[cid]["expected_decision"]
        lines.append(f"| `{cid}` | **{r['stage01'].get('stage01_final_decision')}** | "
                     f"{decision(r, 'full')} | {gt} |")
    lines.append("")
    lines.append(f"Baseline positive control: the frozen Stage01 pair ACCEPTED "
                 f"{len([c for c in accepted if c in truth_success])} of the "
                 f"{n_s} ground-truth successes → the baseline is **not a strawman**.")
    lines.append("")
    false_accept = [c for c in accepted if c in truth_failure]
    lines.append(f"**Stage01 false attributions: {len(false_accept)}/{n_f}** — "
                 f"{', '.join('`'+c+'`' for c in false_accept) if false_accept else 'none'}.")
    lines.append("")
    out["stage01"] = {"applicable": len(applicable), "accepted": accepted,
                      "false_acceptances": false_accept}
    out["set1_crypto_truth"] = set1
    out["set2_attribution_truth"] = set2
    out["set3_family"] = set3

    OUT_MD.write_text("\n".join(lines) + "\n")
    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("\n".join(lines))
    print(f"\n[stage1] wrote {OUT_MD} and {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
