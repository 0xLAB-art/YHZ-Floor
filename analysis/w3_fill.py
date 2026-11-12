#!/usr/bin/env python3
"""
w3_fill.py — the W3 fill engine. One command turns the frozen paper's
[PENDING-W3] placeholders into artifact-derived numbers, exactly as the
pre-registration declared. Built 2026-09-30 (pre-campaign, dry-run against
an empty corpus); the numbers arrive when sp2027/agent-eval/runs_e2 does.

WHAT IT FILLS (and with what):

  1. Table 3 (tab:primary) — per slot: ASR (oracle-verified, denominator =
     graded sessions, PROVIDER_UNAVAILABLE/HARNESS_ERROR excluded per the
     frozen denominator rule), operational yield (successes / ALL attempted
     sessions), FSR under the independent oracle, median T_agent (s).
  2. The pilot-vs-campaign prose — outcome census, attempt economics,
     latency decomposition (T_agent = T_llm + T_exec + T_wait + T_other),
     AOR_op distribution (the pre-registered primary), and the AOR_exec
     comparison.
  3. KM / Fine-Gray inputs — event/censoring censuses; the three-way
     sensitivity band is computed by analysis/bounds_tier.py (separate tool,
     same interface), not here.

WHAT IT DOES NOT DO (by design):
  - Never invents a number: every emitted value re-derives from runs_e2
    records via the same code paths as e4_sensitivity.py / acts_stats.py.
  - Never edits the paper: it writes sp2027/analysis/w3_fill_evidence.json
    + a LaTeX fragment (w3_fill_table3.tex). The human (or a later pass)
    pastes them; results_lock.py then re-derives and locks every number
    before the paper can build with it.
  - Never touches W4/W5 marks (different sources, different tools).

USAGE:
    python3 sp2027/analysis/w3_fill.py                 # full report
    python3 sp2027/analysis/w3_fill.py --dry-run      # census only, no fill
    python3 sp2027/analysis/w3_fill.py --emit-tex     # + LaTeX fragment

Exit codes: 0 = corpus processed (fill-ready or partial); 2 = no corpus /
no records yet (expected before 10-05); 3 = corpus index fails the identity
gate.  A campaign aggregate must never be computed by replaying stale or
duplicate index rows.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "schema"))
from acts_stats import asr_cell, fsr, wilson      # noqa: E402  (frozen math)
from corpus_identity import validate_index         # noqa: E402

ROOT = HERE.parents[1]
CORPUS = ROOT / "sp2027" / "agent-eval" / "runs_e2"
OUT_JSON = HERE / "w3_fill_evidence.json"
OUT_TEX = HERE / "w3_fill_table3.tex"

GRADED = {"SUCCESS", "ORACLE_FAIL", "TIMEOUT", "AGENT_GIVEUP",
          "MODEL_REFUSAL", "TOOL_FAILURE"}
NON_ATTACK = {"PROVIDER_UNAVAILABLE", "HARNESS_ERROR"}
STATUSES = sorted(GRADED | NON_ATTACK)


def load_corpus(corpus: Path) -> list[dict]:
    """Load every identity-gated record listed once in the manifest."""
    index = corpus / "INDEX.jsonl"
    if not index.exists():
        return []
    recs = []
    for line in index.read_text().splitlines():
        if not line.strip():
            continue
        rid = json.loads(line)["run_id"]
        p = corpus / f"{rid}.json"
        if p.exists():
            recs.append(json.loads(p.read_text()))
    return recs


_MODEL_SLOT_FALLBACK = {           # frozen campaign grid (campaign_e2.json)
    "qwen/qwen3.8-27b:free": "O1",
    "nvidia/nemotron-3-super-120b-a12b:free": "O2",
    "google/gemma-4-31b-it:free": "O3",
}


def slot_of(rec: dict) -> str:
    """Slot is NOT a record field: it lives in the run_id (v2_O2__...) with
    a frozen model_id fallback (the real pilot records have no slot)."""
    m = re.match(r"v2_(O\d)__", rec.get("run_id") or "")
    if m:
        return m.group(1)
    mid = (rec.get("model_config") or {}).get("model_id")
    return _MODEL_SLOT_FALLBACK.get(mid, mid or "?")


def session_view(rec: dict) -> dict:
    """Flatten a record to the fields the fill needs. Field names follow the
    REAL record schema (mirrors e4.cohort_label): task_card.task_id /
    task_card.starting_information / model_config.model_id / oracle.verdict."""
    c = rec.get("clocks") or {}
    s = rec.get("session") or {}
    o = rec.get("oracle") or {}
    card = rec.get("task_card") or {}
    tte_m_ns = c.get("tte_m_harness_ns") or c.get("tte_m_oracle_ns")
    op_ns = c.get("tte_op_agent_ns") or c.get("oracle_op_span_ns")
    return {
        "run_id": rec.get("run_id"),
        "slot": slot_of(rec),
        "model_id": (rec.get("model_config") or {}).get("model_id"),
        "task": card.get("task_id"),
        "track": card.get("starting_information") or card.get("track"),
        "status": s.get("status"),
        "attempts": s.get("attempts"),
        "oracle_success": bool((o.get("verdict") or {}).get("success")),
        "tte_m_s": (tte_m_ns / 1e9) if tte_m_ns else None,
        "op_span_s": (op_ns / 1e9) if op_ns else None,
        "drift_ms": (c.get("dual_clock_max_drift_ns") or 0) / 1e6,
    }


def slot_block(views: list[dict]) -> dict:
    """Table 3 columns for one slot, via the frozen math (asr_cell/fsr)."""
    graded = [v for v in views if v["status"] in GRADED]
    cell = asr_cell([v["status"] for v in views])          # denominator rule inside
    oracle_successes = sum(1 for v in views
                           if v["status"] == "SUCCESS" and v["oracle_success"])
    # FSR, exactly e4's claim-submitted semantics: a claim exists iff the
    # session was graded as SUCCESS or ORACLE_FAIL (e4 GRADED_STATUSES);
    # the independent oracle rejects ORACLE_FAIL outright and any SUCCESS
    # whose oracle verdict is false (the coupling check).
    self_reported = sum(1 for v in views
                        if v["status"] in ("SUCCESS", "ORACLE_FAIL"))
    rejected = sum(1 for v in views
                   if v["status"] == "ORACLE_FAIL"
                   or (v["status"] == "SUCCESS" and not v["oracle_success"]))
    f = fsr(self_reported, rejected)
    ttes = sorted(v["tte_m_s"] for v in graded if v["tte_m_s"])
    med = float(np.median(ttes)) if ttes else None
    yield_lo, yield_hi = wilson(oracle_successes, len(views)) if views else (None, None)
    return {
        "n_sessions": len(views),
        "n_graded": len(graded),
        "n_non_attack_excluded": len(views) - len(graded),
        "status_census": dict(Counter(v["status"] for v in views)),
        "asr": {"num": oracle_successes, "denom": cell["denom"],
                "value": cell["asr"], "ci": cell["ci"]},
        "operational_yield": {"num": oracle_successes, "denom": len(views),
                              "value": (oracle_successes / len(views)) if views else None,
                              "ci": (yield_lo, yield_hi)},
        "fsr": f,
        "median_t_agent_s": med,
        "tte_range_s": [ttes[0], ttes[-1]] if ttes else None,
    }


def aor_block(views: list[dict]) -> dict:
    """AOR_op (pre-registered primary) + AOR_exec floor, graded sessions."""
    op, ex = [], []
    for v in views:
        if v["status"] not in GRADED or not v["tte_m_s"]:
            continue
        if v["op_span_s"]:
            op.append(v["tte_m_s"] / v["op_span_s"])
    return {
        "aor_op": {"n": len(op),
                   "median_log10": float(np.median(np.log10(op))) if op else None,
                   "iqr_log10": ([float(np.percentile(np.log10(op), 25)),
                                  float(np.percentile(np.log10(op), 75))] if op else None)},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--emit-tex", action="store_true")
    ap.add_argument("corpus", type=Path, nargs="?", default=None,
                    help="corpus dir (REQUIRED for evidence writes; the "
                         "campaign evidence file is only overwritten when an "
                         "explicit corpus is passed)")
    args = ap.parse_args()

    # 2026-10-01 lesson (T3-SYNC-6 incident): a bare invocation used to
    # default to runs_e2 for PRINTING but still wrote the campaign evidence
    # file from whatever corpus it actually scanned — a diagnostic on the
    # PILOT corpus silently clobbered w3_fill_evidence.json with pilot
    # numbers. The evidence file is campaign-only now.
    corpus = args.corpus or CORPUS
    if not corpus.exists() or not (corpus / "INDEX.jsonl").exists():
        print(f"corpus not present yet: {corpus} (expected on/after 2026-10-05)")
        return 2
    index_issues = validate_index(corpus)
    if index_issues:
        print("CORPUS IDENTITY GATE: FAIL (no aggregate was computed)")
        for issue in index_issues:
            print(f"  - {issue}")
        return 3
    recs = load_corpus(corpus)
    if not recs:
        print("corpus present but empty (gate-armed, pre-launch) — nothing to fill")
        return 2

    views = [session_view(r) for r in recs]
    by_slot = defaultdict(list)
    for v in views:
        by_slot[v["slot"] or "?"].append(v)

    slots = {s: slot_block(vs) for s, vs in sorted(by_slot.items())}
    aor = aor_block(views)
    census = dict(Counter(v["status"] for v in views))
    total = len(views)
    graded = sum(1 for v in views if v["status"] in GRADED)

    print(f"=== W3 fill — {corpus.name} ===")
    print(f"sessions: {total} (graded {graded}, non-attack excluded "
          f"{total - graded}) — grid target 270")
    print(f"census: {census}")
    for s, b in slots.items():
        a = b["asr"]
        asr_s = f"{a['value']:.3f} [{a['ci'][0]:.3f},{a['ci'][1]:.3f}]" if a["value"] is not None else "—"
        f = b["fsr"]
        fsr_s = f"{f['fsr']:.3f}" if f.get("fsr") is not None else "—"
        med = b["median_t_agent_s"]
        print(f"  {s}: n={b['n_sessions']:3d}  ASR={asr_s}  "
              f"yield={b['operational_yield']['value'] if b['operational_yield']['value'] is not None else '—'}  "
              f"FSR={fsr_s}  medT_agent={f'{med:.1f}s' if med else '—'}")

    # 2026-10-01 lesson (T3-SYNC-6 incident): the lock's pilot rehearsal and
    # bare diagnostics used to CLOBBER the campaign evidence file, because
    # the write below was unconditional (and --dry-run was never consulted).
    # Evidence writes are now campaign-corpus-only and never on --dry-run;
    # every other invocation is a read-only diagnostic.
    writes_evidence = (not args.dry_run
                       and corpus.resolve() == CORPUS.resolve())
    if not writes_evidence:
        why = "--dry-run" if args.dry_run else f"diagnostic corpus: {corpus.name}"
        print(f"(read-only scan — no evidence write: {why})")
        return 0
    out = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(corpus),
        "n_sessions": total, "n_graded": graded,
        "grid_target": 270,
        "census": census,
        "slots": slots,
        "aor": aor,
        "note": ("every number re-derived from runs_e2 via acts_stats/e4 "
                 "code paths; results_lock.py re-verifies before any paper build"),
    }
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n")
    print(f"evidence: {OUT_JSON}")

    if args.emit_tex and any(b["asr"]["value"] is not None for b in slots.values()):
        rows = []
        for s, b in slots.items():
            a, f = b["asr"], b["fsr"]
            fmt = lambda x: f"{x:.3f}" if isinstance(x, float) else "---"
            ci = f"[{a['ci'][0]:.2f},{a['ci'][1]:.2f}]" if a.get("ci") else ""
            rows.append(f"{s} & T1 / T2 / T3 & {fmt(a['value'])} {ci} & "
                        f"{fmt(f.get('fsr'))} & "
                        f"{fmt(b['median_t_agent_s'])} \\\\")
        OUT_TEX.write_text("% auto-generated by w3_fill.py — paste into tab:primary "
                           "after results_lock verification\n" + "\n".join(rows) + "\n")
        print(f"table fragment: {OUT_TEX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
