#!/usr/bin/env python3
"""Label-selection + route-identity probe (NOT evidence) for P010L4.

Step zero of the corrected discipline (post-X1): before any freeze, establish
(1) the new key's attested model list, (2) that the opus label is reachable,
and (3) -- the X1 lesson -- that the RAW RESPONSE's own model field echoes the
requested label on this route. Generic single-turn calls, no fixture, no cell
slots, no oracle: unusable as evidence by construction. Recorded in
HEALTH.json + BUDGET_LEDGER.jsonl (non-evidence lines).
"""

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(RESEARCH))

TARGET_LABEL = "claude-opus-5-5"

# load .env into process env (adapter also self-loads, but be explicit)
for line in (ROOT / ".env").read_text().splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

import provider_adapter_agentrouter as adapter  # noqa: E402 (frozen transport)

out = {"role": "label-selection + route-identity probe, NOT evidence",
       "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "steps": []}

# 1. attested model list under the NEW key
p = adapter.ClaudeProvider()
att = p.attest()
out["attested_model_ids"] = att.get("provider_model_ids")
out["attest_http"] = att.get("http_status")
out["steps"].append({"step": "attest", "ok": att.get("http_status") == 200})

# 2. opus reachability + raw-model echo (the X1 lesson)
os.environ["AGENTROUTER_LABEL_MODEL"] = TARGET_LABEL
p2 = adapter.ClaudeProvider(model=TARGET_LABEL)
try:
    t0 = time.time()
    resp = p2.call("Reply with the single word: ok", 32)
    raw = getattr(resp, "raw_body", None) or ""
    echo = None
    try:
        echo = json.loads(raw).get("model")
    except Exception:  # noqa: BLE001
        pass
    out["steps"].append({
        "step": "opus_smoke",
        "ok": True,
        "raw_model_echo": echo,
        "echo_matches_label": echo == TARGET_LABEL,
        "latency_s": round(time.time() - t0, 2),
        "usage": getattr(resp, "usage", None) and {
            k: getattr(resp.usage, k, None) for k in ("input_tokens", "output_tokens")
        } or None,
    })
except adapter.ProviderFailure as e:
    out["steps"].append({"step": "opus_smoke", "ok": False,
                         "provider_failure": str(e)[:200]})
except Exception as e:  # noqa: BLE001
    out["steps"].append({"step": "opus_smoke", "ok": False, "error": str(e)[:200]})

out["route_identity_confirmed"] = any(
    s.get("step") == "opus_smoke" and s.get("echo_matches_label")
    for s in out["steps"])

(HERE / "HEALTH.json").write_text(json.dumps(out, indent=1) + "\n")
with (RESEARCH / "BUDGET_LEDGER.jsonl").open("a") as f:
    f.write(json.dumps({
        "date": out["date"], "namespace": HERE.name,
        "role": "auth_smoke_non_evidence", "protocol": "P010L4-probe",
        "model": TARGET_LABEL, "route_identity_confirmed":
            out["route_identity_confirmed"],
    }) + "\n")
print(json.dumps(out, indent=1))
