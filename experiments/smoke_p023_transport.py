#!/usr/bin/env python3
"""Pre-registration smoke test for the P023 transport layer.

Runs BEFORE any seed is drawn for P023 and uses NO P023 instance: the prompts
are neutral coding requests, so nothing here is a data point for the cohort.
Purpose: measure the end-to-end completion rate and the transport-failure rate
of the retry layer, and record every failed attempt with status and body.

Usage: python3 smoke_p023_transport.py [n]
Writes smoke_p023_transport.json next to this file.
"""
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import provider_adapter_agentrouter_p023 as adapter  # noqa: E402


SHORT = "Reply with exactly one JSON object: {\"ok\": true}. No prose."
# A long, withheld-style request: same shape as the sessions that failed in P021
# (large output budget, program-writing, no stated premise), but no fixture data.
LONG = (
    "Write complete Python source that prints exactly one JSON object with a "
    "key 'value' whose value is the integer 42. Allowed imports are json and "
    "sys. Return exactly one JSON object with a code string and no prose. "
    "Consider the alternatives before answering, then commit to one program."
)


def main(argv):
    n = int(argv[1]) if len(argv) > 1 else 12
    log = HERE / "smoke_p023_failures.jsonl"
    if log.exists():
        log.unlink()
    import os
    os.environ["ACTS_FAILURE_LOG"] = str(log)

    provider = adapter.ClaudeProvider()
    rows = []
    for i in range(n):
        prompt = SHORT if i % 3 == 0 else LONG
        started = time.time()
        row = {"i": i, "prompt_kind": "short" if prompt is SHORT else "long"}
        try:
            result = provider.call(prompt, 1400, timeout=300)
            meta = result["metadata"]
            row.update({"outcome": "OK", "attempts": meta.get("p023_attempt"),
                        "http_status": meta.get("http_status"),
                        "latency_s": round(time.time() - started, 1),
                        "output_tokens": (meta.get("usage") or {}).get("output_tokens"),
                        "text_chars": len(result["text"])})
        except adapter.ProviderFailure as exc:
            row.update({"outcome": "FAIL", "category": exc.category,
                        "http_status": exc.http_status,
                        "latency_s": round(time.time() - started, 1)})
        rows.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)

    ok = [r for r in rows if r["outcome"] == "OK"]
    lat = [r["latency_s"] for r in ok]
    summary = {
        "adapter_sha256": hashlib.sha256(Path(adapter.__file__).read_bytes()).hexdigest(),
        "calls": n,
        "completed": len(ok),
        "completion_rate": round(len(ok) / n, 4),
        "failure_categories": {},
        "attempts_used": sorted({r.get("attempts") for r in ok}),
        "latency_s_median": round(statistics.median(lat), 1) if lat else None,
        "policy": adapter.P023_POLICY,
        "rows": rows,
    }
    for r in rows:
        if r["outcome"] == "FAIL":
            summary["failure_categories"][r["category"]] = \
                summary["failure_categories"].get(r["category"], 0) + 1
    (HERE / "smoke_p023_transport.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"},
                     indent=2, sort_keys=True))
    return 0 if len(ok) == n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
