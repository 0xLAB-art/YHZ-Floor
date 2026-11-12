#!/usr/bin/env python3
"""AUTH_SMOKE for Amendment-4 — one tiny call per registered label.
NON-EVIDENCE (evidence=false): 16-token completions, no task content,
recorded in HEALTH.json.  Verifies transport + auth + label echo only.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from agentrouter_client import AgentRouterClient  # noqa: E402
from run_amend4_sessions import TEMP_BY_LABEL  # noqa: E402 — registered policy

LABELS = ["gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-sol"]
BASE_URL = "https://agentrouter.org"


def main():
    key = os.environ.get("AGENTROUTER_API_KEY", "").strip()
    if not key:
        sys.exit("AGENTROUTER_API_KEY missing")
    results = []
    ok = 0
    for label in LABELS:
        client = AgentRouterClient(key, label, BASE_URL, TEMP_BY_LABEL.get(label))
        rec = {"label": label, "evidence": False}
        try:
            r = client.call("Reply with the single word OK.", 16, timeout=120)
            rec["ok"] = True
            rec["finish_reason"] = r["metadata"]["finish_reason"]
            rec["model_echo"] = r["metadata"].get("model_echo")
            rec["text_head"] = (r["text"] or "")[:24]
            rec["usage"] = r["metadata"].get("usage")
            ok += 1
        except Exception as exc:
            rec["ok"] = False
            rec["error"] = f"{type(exc).__name__}: {exc}"[:200]
        results.append(rec)
    out = {"schema": "external-admission-amend4-health/1",
           "evidence": False,
           "recorded_labels": LABELS,
           "ok_count": ok,
           "results": results}
    (HERE / "HEALTH.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"ok_count": ok, "labels": len(LABELS)}))
    return 0 if ok == len(LABELS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
