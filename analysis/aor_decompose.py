#!/usr/bin/env python3
"""
aor_decompose.py — AOR + TTE_M decomposition over a session corpus
(E2.yaml clocks section: "TTE_M = T_model + T_tools + T_exec + T_oracle +
T_wait_retry (per-request stamps)").

Per session (from the corpus record + its transcript):

  TTE_M      clocks.tte_m_harness_ns            (agent-inclusive wall clock)
  T_llm      Σ llm_span_ns over llm_turns       (model time AS MEASURED —
             includes the loop's in-turn backoff sleeps on retrying turns)
  T_wait     120 s × (# gateway_transient-failed turns) — the exact sleep
             total of a terminal transient turn (3 attempts × 20/40/60 s);
             a strict lower bound for in-turn retry waits overall
  T_exec     Σ run_span_ns over run entries      (agent code execution)
  T_other    TTE_M − T_llm − T_exec (≥0)        (container lifecycle, relay,
             oracle I/O, harness overhead — the T_tools+T_oracle residual)

  AOR variants (log10(TTE_M / TTE_OP)):
    aor_agent  TTE_OP = agent-reported OPSPAN_NS (clocks.tte_op_agent_ns)
               — the pre-registered primary when the agent emits it
    aor_exec   TTE_OP = T_exec — execution-only floor, always computable
               for sessions that ran code; disclosed as a conservative
               variant (overstates AOR vs a true operation span)

Usage:
    python3 sp2027/analysis/aor_decompose.py                     # runs_e2
    python3 sp2027/analysis/aor_decompose.py <corpus_dir>        # e.g. W2 pilot

Output: printed report + sp2027/analysis/aor_<corpusname>.json
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "schema"))
from corpus_identity import require_valid_index  # noqa: E402
TRANSIENT_TURN_SLEEP_S = 120.0     # 3 attempts × (20+40+60) s, exact
GRADED = {"SUCCESS", "ORACLE_FAIL", "TIMEOUT", "AGENT_GIVEUP",
          "MODEL_REFUSAL", "TOOL_FAILURE"}


def load_session(corpus: Path, rid: str):
    rec_p = corpus / f"{rid}.json"
    if not rec_p.exists():
        return None, None
    rec = json.loads(rec_p.read_text())
    tr_p = corpus / "transcripts" / rid / "transcript.jsonl"
    log = []
    if tr_p.exists():
        for line in tr_p.read_text().splitlines():
            try:
                log.append(json.loads(line))
            except Exception:
                pass
    return rec, log


def decompose_one(rec: dict, log: list) -> dict | None:
    c = rec.get("clocks") or {}
    tte_m_ns = c.get("tte_m_harness_ns") or c.get("tte_m_oracle_ns")
    if not tte_m_ns:
        return None
    tte_m = tte_m_ns / 1e9

    t_llm = sum(e["llm_span_ns"] for e in log
                if e.get("type") == "llm_turn" and e.get("llm_span_ns")) / 1e9
    n_transient = sum(1 for r in (rec.get("model_config") or {})
                      .get("request_records") or []
                      if r.get("error_class") == "gateway_transient")
    t_wait = TRANSIENT_TURN_SLEEP_S * n_transient
    t_exec = sum(e["run_span_ns"] for e in log
                 if e.get("type") == "run" and e.get("run_span_ns")) / 1e9
    t_other = tte_m - t_llm - t_exec

    op_agent_ns = c.get("tte_op_agent_ns")
    out = {
        "run_id": rec["run_id"],
        "status": (rec.get("session") or {}).get("status"),
        "tte_m_s": tte_m,
        "t_llm_s": t_llm,
        "t_wait_retry_s": t_wait,
        "t_exec_s": t_exec,
        "t_other_s": max(t_other, 0.0),
        "negative_residual": t_other < -1e-6,
        "op_span_agent_s": (op_agent_ns / 1e9) if op_agent_ns else None,
    }
    if out["op_span_agent_s"]:
        out["aor_agent"] = tte_m / out["op_span_agent_s"]
    if t_exec > 0:
        out["aor_exec"] = tte_m / t_exec
    return out


def summarize(vals) -> dict:
    a = np.asarray(vals, dtype=float)
    if a.size == 0:
        return {"n": 0}
    return {"n": int(a.size), "median": float(np.median(a)),
            "p25": float(np.percentile(a, 25)),
            "p75": float(np.percentile(a, 75)),
            "min": float(a.min()), "max": float(a.max())}


def main() -> int:
    corpus = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        ROOT / "sp2027" / "agent-eval" / "runs_e2"
    index = corpus / "INDEX.jsonl"
    if not index.exists():
        print(f"no corpus at {corpus}")
        return 2
    try:
        require_valid_index(corpus, "AOR/TTE decomposition")
    except RuntimeError as exc:
        print(exc)
        return 3

    rows = []
    for line in index.read_text().splitlines():
        try:
            rid = json.loads(line)["run_id"]
        except Exception:
            continue
        rec, log = load_session(corpus, rid)
        d = decompose_one(rec, log) if rec else None
        if d:
            rows.append(d)

    graded = [r for r in rows if r["status"] in GRADED]
    print(f"=== AOR / TTE_M decomposition — {corpus.name} ===")
    print(f"sessions decomposed: {len(rows)} ({len(graded)} graded)")

    if graded:
        print("\n-- component seconds (graded, full distribution) --")
        for comp in ("tte_m_s", "t_llm_s", "t_wait_retry_s", "t_exec_s",
                     "t_other_s"):
            s = summarize([r[comp] for r in graded])
            print(f"  {comp:14s}: median {s['median']:8.2f}  "
                  f"[{s['p25']:8.2f}–{s['p75']:8.2f}]  "
                  f"min {s['min']:8.2f}  max {s['max']:9.2f}")
        shares = {}
        for comp in ("t_llm_s", "t_wait_retry_s", "t_exec_s", "t_other_s"):
            sh = [r[comp] / r["tte_m_s"] for r in graded if r["tte_m_s"] > 0]
            s = summarize(sh)
            shares[comp] = {"median_share": s.get("median")}
            print(f"  share {comp:9s}: median {s.get('median', 0):6.1%}")
        neg = [r["run_id"] for r in graded if r["negative_residual"]]
        if neg:
            print(f"  ! negative residual (decomposition exceeds TTE_M) in "
                  f"{len(neg)} rows — clock skew or missing spans: {neg[:3]}")

        print("\n-- AOR variants (graded) --")
        a_agent = [r["aor_agent"] for r in graded if r.get("aor_agent")]
        a_exec = [r["aor_exec"] for r in graded if r.get("aor_exec")]
        if a_agent:
            la = np.log10(a_agent)
            print(f"  aor_agent (OPSPAN-reported): n={len(a_agent)}  "
                  f"median log10 {np.median(la):.2f} "
                  f"[{np.percentile(la, 25):.2f}–{np.percentile(la, 75):.2f}]")
        else:
            print("  aor_agent: no agent-reported OPSPAN_NS rows — the "
                  "pre-registered primary lands with W3 agents that emit it")
        if a_exec:
            le = np.log10(a_exec)
            print(f"  aor_exec  (execution floor): n={len(a_exec)}  "
                  f"median log10 {np.median(le):.2f} "
                  f"[{np.percentile(le, 25):.2f}–{np.percentile(le, 75):.2f}]")

    out = HERE / f"aor_{corpus.name}.json"
    out.write_text(json.dumps({
        "corpus": str(corpus), "n_decomposed": len(rows),
        "n_graded": len(graded), "rows": rows}, indent=2) + "\n")
    print(f"\nevidence: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
