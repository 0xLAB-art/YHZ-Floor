#!/usr/bin/env python3
"""H1-R3 analysis.  Applies the preregistered rules in H1R3_PREREGISTRATION.md §8.

No provider calls.  Reads only retained session records.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import h1r3_stats as st

MARGIN = 0.10
ALPHA = 0.05
EXCLUDED_FROM_PAIRED = {"PROVIDER_FAILURE", "EXTRACTION_EMPTY"}
ARMS = ("R0", "R1", "R2")
LEVELS = ("L1", "L2", "L3")
FAMILIES = ("XOR_Keystream_Reuse", "ECDSA_Nonce_Reuse")


def load(run_dir: Path) -> list[dict]:
    return [json.loads(line) for line in (run_dir / "results.jsonl").read_text().splitlines()]


def primary_index(rows: list[dict]) -> dict:
    """(family, level, instance_id, arm) -> the single primary-kind row."""
    index = {}
    for row in rows:
        if row.get("kind") != "primary":
            continue
        index[(row["family"], row["level"], row["instance_id"], row["arm"])] = row
    return index


def collect_pairs(index: dict, level: str, family: str | None, arm: str) -> tuple[list[tuple[dict, dict]], list[dict]]:
    pairs, dropped = [], []
    instances = sorted({k[2] for k in index if k[1] == level and (family is None or k[0] == family)})
    for instance in instances:
        fam = next(k[0] for k in index if k[2] == instance)
        ref = index.get((fam, level, instance, "R0"))
        trt = index.get((fam, level, instance, arm))
        if ref is None or trt is None:
            dropped.append({"instance": instance, "reason": "missing-arm", "arm": arm})
            continue
        if ref.get("terminal") in EXCLUDED_FROM_PAIRED or trt.get("terminal") in EXCLUDED_FROM_PAIRED:
            dropped.append({"instance": instance, "reason": "excluded-terminal", "arm": arm,
                            "ref": ref.get("terminal"), "trt": trt.get("terminal")})
            continue
        pairs.append((ref, trt))
    return pairs, dropped


def outcome(row: dict) -> int:
    return int(bool(row.get("terminal_success")))


def contrast(pairs: list[tuple[dict, dict]], dropped: list[dict]) -> dict:
    if not pairs:
        return {"n": 0, "status": "NOT_ESTIMABLE", "dropped": dropped}
    numeric = [(outcome(r), outcome(t)) for r, t in pairs]
    ci = st.paired_risk_difference_ci(numeric, resamples=20000, seed=20261019)
    ci["equivalence"] = st.equivalence_assessment(ci, MARGIN)
    ci["dropped"] = dropped
    if ci["discordant_ref_only"] + ci["discordant_treat_only"] == 0:
        ci["zero_discordance_bound"] = {
            "n": ci["n"],
            "one_sided_95_upper_bound_on_abs_tau": round(1 - 0.025 ** (1 / ci["n"]), 4),
            "note": "zero discordant pairs; bootstrap interval is degenerate, use this exact bound",
        }
    # Stage attribution for discordant pairs
    ref_only = [(r, t) for r, t in pairs if outcome(r) == 1 and outcome(t) == 0]
    trt_only = [(r, t) for r, t in pairs if outcome(r) == 0 and outcome(t) == 1]
    ci["discordant_detail"] = {
        "ref_only": [{"family": t["family"], "instance": t["instance_id"],
                      "treatment_stage": t.get("terminal"),
                      "treatment_schema_errors": t.get("output_schema_errors"),
                      "treatment_qualification": (t.get("qualification") or {}).get("violations"),
                      "treatment_stderr": (t.get("stderr_tail") or "")[:400],
                      "generalization_success": (t.get("generalization") or {}).get("success")}
                     for _r, t in ref_only],
        "treat_only": [{"family": r["family"], "instance": r["instance_id"],
                        "reference_stage": r.get("terminal"),
                        "reference_stderr": (r.get("stderr_tail") or "")[:400]}
                       for r, _t in trt_only],
    }
    ci["stage_attribution"] = dict(Counter(t.get("terminal") for _r, t in ref_only))
    return ci


def stage_counts(rows: list[dict], arm: str, level: str | None = None) -> dict:
    subset = [r for r in rows if r.get("arm") == arm and r.get("kind") == "primary"
              and (level is None or r.get("level") == level)]
    return dict(Counter(r.get("terminal") for r in subset))


def legacy_success(row: dict) -> int:
    """Counterfactual terminal success under the historical import policy."""
    if row.get("legacy_would_reject"):
        return 0
    return int(bool(row.get("terminal_success")))


def main() -> int:
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "runs" / "confirmatory"
    rows = load(run_dir)
    index = primary_index(rows)
    report: dict = {"run_dir": str(run_dir), "sessions_total": len(rows), "margin": MARGIN, "alpha": ALPHA}

    report["terminal_counts"] = dict(Counter(r.get("terminal") for r in rows))
    report["by_kind"] = {k: dict(Counter(r.get("terminal") for r in rows if r.get("kind") == k))
                         for k in sorted({r.get("kind") for r in rows})}
    report["provider"] = {
        "models": dict(Counter(r.get("provider_model") for r in rows)),
        "http_status": dict(Counter(str(r.get("http_status")) for r in rows)),
        "finish_reasons": dict(Counter(str(r.get("finish_reason")) for r in rows)),
        "total_input_tokens": sum((r.get("usage") or {}).get("input_tokens", 0) for r in rows),
        "total_output_tokens": sum((r.get("usage") or {}).get("output_tokens", 0) for r in rows),
        "cache_read_tokens": sum((r.get("usage") or {}).get("cache_read_input_tokens", 0) for r in rows),
        "distinct_source_hashes": len({r.get("source_sha256") for r in rows if r.get("source_sha256")}),
        "distinct_prompts": len({r.get("prompt_sha256") for r in rows}),
    }

    # ---- contrasts --------------------------------------------------------
    contrasts, holm_inputs, legacy_contrasts = {}, [], {}
    for level in LEVELS:
        for arm in ("R1", "R2"):
            pairs, dropped = collect_pairs(index, level, None, arm)
            key = f"{level}|{arm}_vs_R0|pooled"
            contrasts[key] = contrast(pairs, dropped)
            if level == "L3" and contrasts[key].get("mcnemar"):
                holm_inputs.append((key, contrasts[key]["mcnemar"]["p_value"]))
            if pairs:
                legacy_numeric = [(legacy_success(r), legacy_success(t)) for r, t in pairs]
                legacy_contrasts[key] = st.paired_risk_difference_ci(legacy_numeric, resamples=20000, seed=20261019)
        for family in FAMILIES:
            for arm in ("R1", "R2"):
                pairs, dropped = collect_pairs(index, level, family, arm)
                contrasts[f"{level}|{arm}_vs_R0|{family}"] = contrast(pairs, dropped)
    report["contrasts"] = contrasts
    report["primary_holm"] = st.holm(holm_inputs) if holm_inputs else []
    report["legacy_counterfactual_contrasts"] = legacy_contrasts

    # ---- stage decomposition ---------------------------------------------
    report["stage_by_arm"] = {arm: stage_counts(rows, arm) for arm in ARMS}
    report["stage_by_arm_L3"] = {arm: stage_counts(rows, arm, "L3") for arm in ARMS}
    report["terminal_success_by_cell"] = {}
    for level in LEVELS:
        for family in FAMILIES:
            for arm in ARMS:
                subset = [r for r in rows if r.get("kind") == "primary" and r.get("level") == level
                          and r.get("family") == family and r.get("arm") == arm]
                report["terminal_success_by_cell"][f"{level}|{family}|{arm}"] = {
                    "n": len(subset), "success": sum(outcome(r) for r in subset)}

    # ---- legacy import-policy sensitivity --------------------------------
    report["legacy_policy"] = {}
    for arm in ARMS:
        subset = [r for r in rows if r.get("arm") == arm and r.get("kind") == "primary"]
        rejected = [r for r in subset if r.get("legacy_would_reject")]
        report["legacy_policy"][arm] = {
            "n": len(subset),
            "legacy_would_reject": len(rejected),
            "legacy_reject_rate": round(len(rejected) / len(subset), 4) if subset else None,
            "legacy_reject_but_v3_success": sum(1 for r in rejected if r.get("terminal_success") == 1),
        }

    # ---- generalization ---------------------------------------------------
    report["generalization"] = {}
    for arm in ARMS:
        subset = [r for r in rows if r.get("arm") == arm and (r.get("generalization") or {}).get("attempted")]
        report["generalization"][arm] = {
            "attempted": len(subset),
            "succeeded": sum(1 for r in subset if r["generalization"].get("success") == 1),
            "rate": round(sum(1 for r in subset if r["generalization"].get("success") == 1) / len(subset), 4) if subset else None,
        }

    # ---- replicate / noise floor -----------------------------------------
    base_r0 = {(r["family"], r["level"], r["instance_id"]): r for r in rows
               if r.get("kind") == "primary" and r.get("arm") == "R0"}
    replicates = defaultdict(list)
    for row in rows:
        if row.get("kind") == "noise":
            replicates[(row["family"], row["level"], row["instance_id"])].append(row)
    rep_rows = []
    for key, group in replicates.items():
        base = base_r0.get(key)
        members = ([base] if base else []) + sorted(group, key=lambda r: r.get("replicate_index", 0))
        successes = [outcome(m) for m in members]
        sources = [m.get("source_sha256") for m in members]
        rep_rows.append({"instance": key[2], "family": key[0], "level": key[1], "k": len(members),
                         "successes": successes,
                         "all_same_outcome": len(set(successes)) == 1,
                         "distinct_sources": len(set(sources))})
    flat_a, flat_b = [], []
    for r in rep_rows:
        for i in range(r["k"] - 1):
            flat_a.append(r["successes"][i])
            flat_b.append(r["successes"][i + 1])
    report["replicate_noise"] = {
        "cells": len(rep_rows),
        "sessions_in_cells": sum(r["k"] for r in rep_rows),
        "cells_with_unanimous_outcome": sum(1 for r in rep_rows if r["all_same_outcome"]),
        "outcome_agreement_rate": round(sum(1 for r in rep_rows if r["all_same_outcome"]) / len(rep_rows), 4) if rep_rows else None,
        "cells_with_identical_source": sum(1 for r in rep_rows if r["distinct_sources"] == 1),
        "mean_distinct_sources_per_cell": round(sum(r["distinct_sources"] for r in rep_rows) / len(rep_rows), 3) if rep_rows else None,
        "pairwise_outcome_kappa": st.cohens_kappa(flat_a, flat_b) if flat_a else None,
        "source_level_identical_fraction": round(sum(1 for r in rep_rows if r["distinct_sources"] == 1) / len(rep_rows), 4) if rep_rows else None,
        "detail": rep_rows,
    }

    # ---- complexity interaction (descriptive) ----------------------------
    inter_rows = [{"instance": f"{r['family']}|{r['instance_id']}", "arm": r["arm"], "level": r["level"],
                   "terminal_success": outcome(r)}
                  for r in rows if r.get("kind") == "primary" and r.get("arm") in ARMS]
    report["complexity_interaction"] = {
        arm: st.interaction_test([r for r in inter_rows if r["arm"] in ("R0", arm)]) for arm in ("R1", "R2")}

    # ---- C0 control -------------------------------------------------------
    c0_rows = [r for r in rows if r.get("kind") == "c0"]
    report["c0"] = {
        "scheduled": len(c0_rows),
        "correct_abstention": sum(1 for r in c0_rows if r.get("c0_correct_abstention") == 1),
        "terminal_counts": dict(Counter(r.get("terminal") for r in c0_rows)),
        "note": "different predicate; never pooled with the representation contrast",
    }

    out_json = HERE / "H1R3_ANALYSIS.json"
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (HERE / "H1R3_ANALYSIS.md").write_text(render_markdown(report))
    print(json.dumps({k: report[k] for k in ("sessions_total", "terminal_counts", "c0", "replicate_noise")}, indent=2)[:3000])
    print(f"\nwrote {out_json}")
    return 0


def _fmt(v, nd=3):
    return "—" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def render_markdown(report: dict) -> str:
    lines = ["# H1-R3 Confirmatory Analysis", "",
             f"Sessions analysed: **{report['sessions_total']}**  ",
             f"Equivalence margin: **±{report['margin']:.2f}**  ",
             "", "## Session inventory", "", "| Terminal stage | n |", "|---|---:|"]
    for stage, n in sorted(report["terminal_counts"].items(), key=lambda x: -x[1]):
        lines.append(f"| `{stage}` | {n} |")
    lines += ["", "## Terminal success by cell", "",
              "| Level | Family | R0 | R1 | R2 |", "|---|---|---:|---:|---:|"]
    for level in LEVELS:
        for family in FAMILIES:
            cells = []
            for arm in ARMS:
                c = report["terminal_success_by_cell"].get(f"{level}|{family}|{arm}", {"n": 0, "success": 0})
                cells.append(f"{c['success']}/{c['n']}")
            lines.append(f"| {level} | {family} | " + " | ".join(cells) + " |")
    lines += ["", "## Paired contrasts (τ = treatment − R0)", "",
              "| Contrast | n | R0 rate | Tx rate | τ | 95% CI | b (R0-only) | c (tx-only) | McNemar p | Decision |",
              "|---|---:|---:|---:|---:|---|---:|---:|---:|---|"]
    for key in sorted(report["contrasts"]):
        c = report["contrasts"][key]
        if not c.get("n"):
            lines.append(f"| {key} | 0 | — | — | — | — | — | — | — | NOT_ESTIMABLE |")
            continue
        mc = c.get("mcnemar", {})
        lines.append(
            f"| {key} | {c['n']} | {_fmt(c['ref_rate'])} | {_fmt(c['treat_rate'])} | "
            f"{_fmt(c['estimate'])} | [{_fmt(c['ci_low'])}, {_fmt(c['ci_high'])}] | "
            f"{c['discordant_ref_only']} | {c['discordant_treat_only']} | {_fmt(mc.get('p_value'))} | "
            f"{c.get('equivalence', {}).get('status')} |")
    lines += ["", "## Stage attribution of discordant pairs", ""]
    for key in sorted(report["contrasts"]):
        c = report["contrasts"][key]
        att = c.get("stage_attribution") or {}
        if att:
            lines.append(f"- **{key}**: treatment-arm failure stages {json.dumps(att, sort_keys=True)}")
    lines += ["", "## Legacy import policy sensitivity", "",
              "| Arm | n | legacy would reject | rate | would still have succeeded under v3 |",
              "|---|---:|---:|---:|---:|"]
    for arm, v in report["legacy_policy"].items():
        lines.append(f"| {arm} | {v['n']} | {v['legacy_would_reject']} | {_fmt(v['legacy_reject_rate'])} | "
                     f"{v['legacy_reject_but_v3_success']} |")
    lines += ["", "## Generalization to unpublished instances", "",
              "| Arm | attempted | succeeded | rate |", "|---|---:|---:|---:|"]
    for arm, v in report["generalization"].items():
        lines.append(f"| {arm} | {v['attempted']} | {v['succeeded']} | {_fmt(v['rate'])} |")
    rn = report["replicate_noise"]
    lines += ["", "## Sampling-noise floor (exact duplicate prompts)", "",
              f"- cells: {rn['cells']}, sessions: {rn['sessions_in_cells']}",
              f"- cells with unanimous outcome: {rn['cells_with_unanimous_outcome']}"
              f" ({_fmt(rn['outcome_agreement_rate'])})",
              f"- cells with byte-identical programs: {rn['cells_with_identical_source']}"
              f" ({_fmt(rn['source_level_identical_fraction'])})",
              f"- mean distinct programs per cell: {_fmt(rn['mean_distinct_sources_per_cell'])}",
              f"- pairwise outcome kappa: {_fmt(rn['pairwise_outcome_kappa'])}"]
    lines += ["", "## C0 abstention control (separate predicate)", "",
              f"- scheduled {report['c0']['scheduled']}, correct abstention {report['c0']['correct_abstention']}",
              f"- terminal counts {json.dumps(report['c0']['terminal_counts'], sort_keys=True)}"]
    lines += ["", "## Primary Holm adjustment", ""]
    for h in report.get("primary_holm", []):
        lines.append(f"- {h['label']}: p={h['p']:.4f}, p_Holm={h['p_holm']:.4f}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
