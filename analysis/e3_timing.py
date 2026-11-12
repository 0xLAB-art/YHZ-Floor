#!/usr/bin/env python3
"""
e3_timing.py — E3 pre-campaign clock-sensitivity analysis (Table C groundwork).

E3.yaml freezes a 2×2×2×2 timing factorial (2000 trials/cell) to run on the
dedicated timing rig before 2026-10-25. That trial campaign is NOT what this
script does — it cannot be run from logged agent-session data. What this
script does, per the same frozen design, is the PRE-CAMPAIGN half:

  1. INVENTORY — every clock field present in the existing corpora
     (legacy v1 54 rows + W2 pilot 20 rows), with admissibility.
  2. DUAL-CLOCK DRIFT ANALYSIS — the harness-vs-oracle clock agreement
     distribution, split by the drift classes that acts_audit already
     enforces (< 1 ms admissible; the legacy incident rows ~1.1–1.3 s).
     This is the empirical motivation for the frozen 1 ms tolerance and for
     E3's premise that clock choice changes measured outcomes.
  3. TTE_M LANDSCAPE — harness/agent-inclusive timing across sessions
     (legacy graded + W2), the quantity E3's factorial must ultimately
     de-compose into T_model/T_tools/T_exec/T_oracle.
  4. AOR FEASIBILITY — how many rows today carry op-span clocks (TTE_OP)
     for the agent-inclusive/operation-only contrast, and what the pilot
     AOR looks like on the admissible subset (a preview, not a claim).

Outputs: printed report + sp2027/analysis/e3_clock_evidence.json (numbers
only; no raw session data leaves the corpus dirs).

Run:  python3 sp2027/analysis/e3_timing.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from acts_stats import wilson  # noqa: E402  (frozen stats conventions)

CORPORA = {
    "legacy_v1": ROOT / "sp2027" / "agent-eval" / "runs_legacy_v1",
    "w2_pilot": ROOT / "sp2027" / "agent-eval" / "runs_w2_pilot",
}
OUT = HERE / "e3_clock_evidence.json"
TOLERANCE_MS = 1.0          # acts_audit frozen dual-clock tolerance
GRADED = {"SUCCESS", "ORACLE_FAIL", "TIMEOUT", "AGENT_GIVEUP",
          "MODEL_REFUSAL", "TOOL_FAILURE"}


def load_corpus(d: Path):
    for p in sorted(d.glob("*.json")):
        try:
            yield json.loads(p.read_text())
        except Exception:
            continue


def ms(ns) -> float | None:
    return ns / 1e6 if ns else None


def main() -> int:
    ev = {"generated_utc": None, "corpora": {}, "dual_clock_drift": {},
          "tte_m_landscape": {}, "aor_feasibility": {}}
    from datetime import datetime, timezone
    ev["generated_utc"] = datetime.now(timezone.utc).isoformat()

    all_drift = []          # (corpus, run_id, drift_ms, status)
    all_tte_m = []          # (corpus, run_id, tte_m_ms, status)
    aor_rows = []           # (corpus, run_id, tte_m_s, tte_op_s, status)

    for name, d in CORPORA.items():
        rows = list(load_corpus(d))
        dual = op_span = 0
        for r in rows:
            c = r.get("clocks") or {}
            h, o = c.get("tte_m_harness_ns"), c.get("tte_m_oracle_ns")
            status = (r.get("session") or {}).get("status")
            rid = r.get("run_id")
            if h and o:
                dual += 1
                all_drift.append((name, rid, abs(h - o) / 1e6, status))
                tte = ms(max(h, o))
                if tte is not None:
                    all_tte_m.append((name, rid, tte, status))
            if c.get("tte_op_agent_ns") or c.get("oracle_op_span_ns"):
                op_span += 1
                tte_op = ms(c.get("oracle_op_span_ns") or
                            c.get("tte_op_agent_ns"))
                if tte and tte_op and tte_op > 0:
                    aor_rows.append((name, rid, tte / 1e3, tte_op / 1e3,
                                     status))
        ev["corpora"][name] = {
            "rows": len(rows), "dual_clock_rows": dual,
            "op_span_rows": op_span,
            "request_record_rows": sum(
                1 for r in rows if (r.get("model_config") or {})
                .get("request_records"))}

    # ---- 2. dual-clock drift classes -----------------------------------
    within = [x for x in all_drift if x[2] <= TOLERANCE_MS]
    breach = [x for x in all_drift if x[2] > TOLERANCE_MS]
    drift_in = np.array([x[2] for x in within])
    ev["dual_clock_drift"] = {
        "tolerance_ms": TOLERANCE_MS,
        "n_dual": len(all_drift),
        "n_within": len(within),
        "n_breach": len(breach),
        "within_ms": {"median": float(np.median(drift_in)),
                      "p95": float(np.percentile(drift_in, 95)),
                      "max": float(drift_in.max())},
        "breach_ms": sorted(round(x[2], 1) for x in breach),
        "breach_status_counts": dict(
            __import__("collections").Counter(x[3] for x in breach)),
        # per-corpus within-rate with Wilson CIs (proportion of sessions
        # whose dual clocks agree within the frozen tolerance)
        "within_rate": {
            name: (lambda x, n: {"within": x, "n": n, "rate": x / n,
                                 "ci95": wilson(x, n)})(
                sum(1 for c, _, dms, _ in all_drift
                    if c == name and dms <= TOLERANCE_MS),
                sum(1 for c, _, _, _ in all_drift if c == name))
            for name in CORPORA},
    }

    # ---- 3. TTE_M landscape (graded sessions only) ----------------------
    graded_tte = [x for x in all_tte_m if x[3] in GRADED]
    v = np.array([x[2] for x in graded_tte]) / 1e3   # seconds
    ev["tte_m_landscape"] = {
        "n_graded_with_dual_clocks": int(v.size),
        "seconds": {"median": float(np.median(v)),
                    "p25": float(np.percentile(v, 25)),
                    "p75": float(np.percentile(v, 75)),
                    "min": float(v.min()), "max": float(v.max())},
        "by_corpus": {
            name: {"n": int(sum(1 for x in graded_tte if x[0] == name)),
                   "median_s": float(np.median(
                       [x[2] / 1e3 for x in graded_tte if x[0] == name]))}
            for name in CORPORA
            if any(x[0] == name for x in graded_tte)},
        "note": ("agent-inclusive TTE_M; the frozen E3 factorial decomposes "
                 "this into T_model/T_tools/T_exec/T_oracle via the "
                 "component stamps the v2 harness already logs"),
    }

    # ---- 4. AOR feasibility ---------------------------------------------
    admissible = [x for x in aor_rows if x[2] > 0 and x[3] > 0]
    ratios = np.array([x[2] / x[3] for x in admissible])
    ev["aor_feasibility"] = {
        "n_op_span_rows": len(aor_rows),
        "n_admissible_aor": int(ratios.size),
        "preview_log10_aor": {
            "median": float(np.median(np.log10(ratios))) if ratios.size else None,
            "iqr": ([float(np.percentile(np.log10(ratios), 25)),
                     float(np.percentile(np.log10(ratios), 75))]
                    if ratios.size else None)},
        "caveat": ("preview over legacy+ pilot rows only; the frozen E3 "
                   "factorial (2000 trials/cell on the timing rig) is the "
                   "evidence source for Table C — this analysis bounds the "
                   "agent-session side of the contrast and demonstrates the "
                   "pipeline end-to-end"),
    }

    OUT.write_text(json.dumps(ev, indent=2) + "\n")

    # ---- printed report --------------------------------------------------
    print("=== E3 pre-campaign clock evidence ===")
    for name, s in ev["corpora"].items():
        print(f"{name:10s}: {s['rows']} rows · {s['dual_clock_rows']} dual-clock"
              f" · {s['op_span_rows']} op-span · {s['request_record_rows']} req-log")
    dd = ev["dual_clock_drift"]
    print(f"\ndual-clock drift (tolerance {TOLERANCE_MS} ms):")
    print(f"  within : {dd['n_within']}/{dd['n_dual']} "
          f"(median {dd['within_ms']['median']:.3f} ms, "
          f"max {dd['within_ms']['max']:.3f} ms)")
    print(f"  breach : {dd['n_breach']} rows — {dd['breach_ms']}")
    for name, s in dd["within_rate"].items():
        lo, hi = s["ci95"]
        print(f"  {name:10s} within-rate {s['within']}/{s['n']} "
              f"= {s['rate']:.2f} [{lo:.2f}, {hi:.2f}]")
    tl = ev["tte_m_landscape"]
    print(f"\nTTE_M (graded, agent-inclusive): median {tl['seconds']['median']:.1f} s "
          f"[{tl['seconds']['p25']:.1f}–{tl['seconds']['p75']:.1f}], "
          f"range {tl['seconds']['min']:.1f}–{tl['seconds']['max']:.1f} "
          f"(n={tl['n_graded_with_dual_clocks']})")
    af = ev["aor_feasibility"]
    print(f"AOR preview: {af['n_admissible_aor']}/{af['n_op_span_rows']} "
          f"admissible rows")
    print(f"\nevidence: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
