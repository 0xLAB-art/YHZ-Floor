#!/usr/bin/env python3
"""NON-EVIDENCE series probe, new key: pass-rate at the registered 8400 floor.

Six calls at max_tokens=8400 on the frozen CBC turn-1 prompt bytes (seed 441,
A_INTERACTIVE), interleaved after one 32-token control.  Reads the client's
real return shape (text / metadata.finish_reason / metadata.usage).  Prints
per-call status + stop_reason + usage + text head; the raw bodies of the
8400 calls are saved to probe_series_raw/ for the route-behavior record.
Key from env only."""
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from agentrouter_client import AgentRouterClient, ProviderFailure  # noqa: E402

LABEL = "gpt-5.6-sol"
BASE_URL = "https://agentrouter.org"
TEMP = 1.0
PROMPT_FILE = sorted((HERE / "sessions" / "prompts").glob("*A_INTERACTIVE*seed_441*turn1.txt"))[0]
FROZEN_PROMPT = PROMPT_FILE.read_text()
OUT = HERE / "probe_series_raw"
OUT.mkdir(exist_ok=True)
PLAN = [("ctrl", 32)] + [("mt8400", 8400)] * 6


def main():
    key = os.environ.get("AGENTROUTER_API_KEY")
    if not key:
        sys.exit("AGENTROUTER_API_KEY not in environment")
    client = AgentRouterClient(key, LABEL, BASE_URL, TEMP)
    print(f"prompt: {PROMPT_FILE.name} ({len(FROZEN_PROMPT)} bytes)")
    results = []
    for i, (label, budget) in enumerate(PLAN):
        t0 = time.time()
        try:
            resp = client.call(FROZEN_PROMPT, max_tokens=budget, timeout=300)
            meta = resp["metadata"]
            text = resp["text"]
            head = text[:80].replace("\n", " ")
            (OUT / f"{i}_{label}_mt{budget}.json").write_text(resp["raw_body"])
            line = (f"{i} {label} mt={budget}: 200 stop={meta['finish_reason']} "
                    f"in={meta['usage'].get('input_tokens')} "
                    f"out={meta['usage'].get('output_tokens')} "
                    f"{meta['elapsed_s']}s head={head!r}")
            results.append((label, "PASS"))
        except ProviderFailure as exc:
            line = (f"{i} {label} mt={budget}: FAIL "
                    f"category={exc.category} detail={str(exc.detail)[:200]!r}")
            results.append((label, "FAIL"))
        print(line, flush=True)
        time.sleep(5)
    passes = sum(1 for _, s in results if s == "PASS")
    mt8400 = [s for (l, s) in results if l == "mt8400"]
    print(f"SUMMARY: mt8400 {mt8400.count('PASS')}/6 pass; ctrl {'PASS' if results[0][1]=='PASS' else 'FAIL'}")


if __name__ == "__main__":
    main()
