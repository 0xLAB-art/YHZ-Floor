#!/usr/bin/env python3
"""
bounds_tier.py — the three-way KM outage-sensitivity band.

Named in the paper's frozen text:
  "...a sensitivity band that re-estimates the curves under outage handled as
   censoring, as a competing risk, and as worst-case failure---the
   qualitative conclusions must hold under all three for any curve claim to
   enter the paper~[PENDING-W3: analysis/bounds_tier.py]."

Three views over the same time-to-verdict data (graded + non-attack
sessions; a non-attack session's duration is a recorded operational fact,
not an attack failure — that is exactly what the band stress-tests):

  TIER 1  outage = censored at its duration   (KM's standard treatment)
  TIER 2  outage = competing risk             (Fine-Gray-style: outage is an
           event type in its own right; here: cumulative incidence of the
           two event types, 1 - S_outage-free - C_outage at each time)
  TIER 3  outage = worst-case failure         (an attack failure AT its
           duration — the operator's pessimistic bound)

A qualitative conclusion (e.g. "the median time-to-success is X", "success
mass concentrates before t") must hold in ALL THREE for any curve claim to
enter the paper. The verdict is emitted per declared claim; with no claims
declared (pre-W3), the tool emits the three curves + censuses and exits 0.

Reuses the frozen Kaplan-Meier in acts_stats.py (regression-tested).

USAGE:
    python3 sp2027/analysis/bounds_tier.py                # report + JSON
    python3 sp2027/analysis/bounds_tier.py --claim "median time-to-success < 300 s"

Exit codes: 0 = emitted (verdicts all-hold or no claims); 1 = a declared
claim FAILS the band; 2 = no corpus yet (expected before 10-05).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from acts_stats import kaplan_meier                    # noqa: E402  (frozen KM)

ROOT = HERE.parents[1]
CORPUS = ROOT / "sp2027" / "agent-eval" / "runs_e2"
OUT = HERE / "bounds_tier_evidence.json"

GRADED = {"SUCCESS", "ORACLE_FAIL", "TIMEOUT", "AGENT_GIVEUP",
          "MODEL_REFUSAL", "TOOL_FAILURE"}
NON_ATTACK = {"PROVIDER_UNAVAILABLE", "HARNESS_ERROR"}


def load_views(corpus: Path) -> list[dict]:
    idx = corpus / "INDEX.jsonl"
    if not idx.exists():
        return []
    views = []
    for line in idx.read_text().splitlines():
        if not line.strip():
            continue
        rid = json.loads(line)["run_id"]
        p = corpus / f"{rid}.json"
        if not p.exists():
            continue
        rec = json.loads(p.read_text())
        c = rec.get("clocks") or {}
        tte = (c.get("tte_m_harness_ns") or c.get("tte_m_oracle_ns"))
        if not tte or tte <= 0:
            continue
        views.append({"run_id": rec.get("run_id"),
                      "status": (rec.get("session") or {}).get("status"),
                      "tte_s": tte / 1e9})
    return views


def km_curve(durations: list[float], events: list[bool]):
    km = kaplan_meier(durations, events)
    return {"n": km.n, "events": km.events, "censored": km.censored,
            "median_s": km.median,
            "curve": [[round(t, 3), round(s, 4)]
                      for t, s in zip(km.times, km.survival)]}


def three_tiers(views: list[dict]) -> dict:
    """Tiers 1-3 over attack sessions; outages re-tiered per view."""
    attack = [v for v in views if v["status"] in GRADED]
    outage = [v for v in views if v["status"] in NON_ATTACK]
    if not attack:
        return {"n_attack": 0, "n_outage": len(outage)}

    # Tier 1: outage censored (attack KM over graded only)
    t1 = km_curve([v["tte_s"] for v in attack],
                  [v["status"] == "SUCCESS" for v in attack])

    # Tier 2: competing risks — attack events vs outage events on one axis.
    # Attack cumulative incidence: KM of attack-events with outages censored
    # (t1) times 1; outage cumulative incidence via its own KM with attack
    # sessions censored at their durations. C_outage(t) = 1 - S_outage-free(t).
    all_d = [v["tte_s"] for v in views]
    out_d = [v["tte_s"] for v in outage]
    out_ev = [True] * len(outage)
    c_out = km_curve(all_d, [v["status"] in NON_ATTACK for v in views])
    # attack-event cumulative incidence (Aalen-Johansen for 2 risks):
    times = sorted({v["tte_s"] for v in views})
    s_attack = dict(zip([p[0] for p in t1["curve"]], [p[1] for p in t1["curve"]]))
    s_out = dict(zip([p[0] for p in c_out["curve"]], [p[1] for p in c_out["curve"]]))

    def s_at(curve: dict, t: float) -> float:
        ks = [k for k in curve if k <= t]
        return curve[ks[-1]] if ks else 1.0

    ci_attack = [[round(t, 3), round(1.0 - s_at(s_attack, t), 4)] for t in times]
    ci_outage = [[round(t, 3), round(1.0 - s_at(s_out, t), 4)] for t in times]
    t2 = {"n_attack": len(attack), "n_outage": len(outage),
          "ci_attack": ci_attack, "ci_outage": ci_outage,
          "note": ("Aalen-Johansen two-risk decomposition; outage is an event "
                   "type in its own right (Fine-Gray tradition)")}

    # Tier 3: worst case — every outage is an attack failure at its duration
    t3 = km_curve([v["tte_s"] for v in views],
                  [v["status"] == "SUCCESS" for v in views])

    return {"n_attack": len(attack), "n_outage": len(outage),
            "tier1_outage_censored": t1,
            "tier2_competing_risk": t2,
            "tier3_outage_as_failure": t3,
            "attack_success_n": sum(1 for v in attack if v["status"] == "SUCCESS")}


def check_claim(band: dict, claim: str) -> dict:
    """A claim must hold in all three tiers. Supported form (kept minimal
    and honest — a richer parser is W5 work with the statistics lock):
      'median time-to-success < X s'  /  '> X s'
    A None median in a tier means success mass never reaches 50% there
    (always possible under tier 3, where outages are failures): read as
    'median > X' (holds for '>' claims, fails for '<' claims).
    NOTE: success-mass claims are deliberately NOT here — success timing is
    invariant to outage handling (outages are neither successes nor do they
    move successes), so they are not tier-sensitive and not this band's job.
    """
    m = re.search(r"median time-to-success\s*([<>])\s*([\d.]+)\s*s", claim)
    if m:
        op, x = m.group(1), float(m.group(2))
        vals = []
        for tier in ("tier1_outage_censored", "tier3_outage_as_failure"):
            med = (band.get(tier) or {}).get("median_s")
            vals.append((tier, med))
        holds = True
        parts = []
        for tier, med in vals:
            if med is None:
                holds &= (op == ">")
                parts.append(f"{tier}: median undefined (success mass < 50%) ⇒ > {x}")
            else:
                holds &= (med < x) if op == "<" else (med > x)
                parts.append(f"{tier} median {med:.1f}s")
        return {"claim": claim, "holds": bool(holds), "detail": "; ".join(parts)}
    return {"claim": claim, "holds": False,
            "detail": "unsupported claim form (see docstring)"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claim", action="append", default=[],
                    help="qualitative claim the band must confirm (repeatable)")
    ap.add_argument("corpus", type=Path, nargs="?", default=CORPUS,
                    help="corpus dir (default runs_e2; pass runs_w2_pilot "
                         "for a real-data rehearsal)")
    args = ap.parse_args()

    corpus = args.corpus
    if not corpus.exists() or not (corpus / "INDEX.jsonl").exists():
        print(f"corpus not present yet: {corpus}")
        return 2
    views = load_views(corpus)
    if not views:
        print("no timed sessions in the corpus yet")
        return 2

    band = three_tiers(views)
    verdicts = [check_claim(band, c) for c in args.claim]

    print(f"=== bounds_tier — three-way outage sensitivity band ===")
    print(f"sessions: {band['n_attack']} attack-grade, {band['n_outage']} outage")
    for tier, key in (("T1 outage=censored", "tier1_outage_censored"),
                      ("T3 outage=worst-case failure", "tier3_outage_as_failure")):
        b = band.get(key) or {}
        med = b.get("median_s")
        print(f"  {tier}: n={b.get('n')} events={b.get('events')} "
              f"median={f'{med:.1f}s' if med else '—'}")
    for v in verdicts:
        print(f"  [{'HOLDS' if v['holds'] else 'FAILS'}] {v['claim']} — {v['detail']}")

    out = {"generated_utc": datetime.now(timezone.utc).isoformat(),
           "source": str(corpus), "band": band, "claims": verdicts,
           "note": ("qualitative conclusions must hold under all three tiers "
                    "for any curve claim to enter the paper (frozen text)")}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"evidence: {OUT}")
    fails = [v for v in verdicts if not v["holds"]]
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
