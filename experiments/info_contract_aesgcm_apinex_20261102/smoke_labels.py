#!/usr/bin/env python3
"""Pre-registration smoke probe for the P015 cross-family labels.

NOT an experiment call: one short off-fixture prompt per label ("reply with a
single token") to confirm (a) the key authenticates, (b) the label is served,
(c) text comes back inside the call timeout, (d) the adapter's metadata fields
are populated. No fixture, no cell slot, no oracle is involved, so nothing here
can be counted as a session in any cohort.

Output: info_contract_aesgcm_apinex_20261102/smoke/labels_smoke_20261102.json
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent          # this namespace
ROOT = HERE.parent                              # research_execution (adapter lives here)
NAMESPACE = HERE
SMOKE_PROMPT = "Reply with exactly one word: READY"
LABELS = ["claude-opus-5.5", "gemini-3.1-pro"]


def main():
    sys.path.insert(0, str(ROOT))
    import provider_adapter_apinex_l6 as adapter  # noqa: E402

    out = {"probe": "p015-label-smoke-20261102",
           "purpose": "pre-registration reachability/format check; NOT an experiment call",
           "prompt": SMOKE_PROMPT, "labels": [], "started": time.time()}
    (NAMESPACE / "smoke").mkdir(parents=True, exist_ok=True)
    for label in LABELS:
        rec = {"label": label, "transport": "apinex/openai_chat_completions"}
        t0 = time.time()
        try:
            provider = adapter.ClaudeProvider(model=label)
            res = provider.call(SMOKE_PROMPT, max_tokens=64, timeout=300)
            meta = res["metadata"]
            rec.update(status="OK", latency_s=round(time.time() - t0, 1),
                       http_status=meta.get("http_status"),
                       provider_model=meta.get("provider_model"),
                       finish_reason=meta.get("finish_reason"),
                       max_tokens_sent=meta.get("max_tokens_sent"),
                       usage=meta.get("usage"),
                       output_head=(res["text"] or "")[:80])
        except adapter.ProviderFailure as exc:
            rec.update(status=exc.category, latency_s=round(time.time() - t0, 1),
                       error=str(exc)[:300],
                       http_status=getattr(exc.response, "status_code", None))
        except Exception as exc:  # noqa: BLE001 — smoke probe must never crash the batch
            rec.update(status="SMOKE_EXCEPTION", latency_s=round(time.time() - t0, 1),
                       error=f"{type(exc).__name__}: {exc}"[:300])
        out["labels"].append(rec)
        print(json.dumps(rec, indent=2, sort_keys=True), flush=True)
    out["finished"] = time.time()
    (NAMESPACE / "smoke" / "labels_smoke_20261102.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    ok = [r["label"] for r in out["labels"] if r["status"] == "OK"]
    print("\nREACHABLE:", ok, "| FAILED:", [r["label"] for r in out["labels"] if r["status"] != "OK"])


if __name__ == "__main__":
    main()
