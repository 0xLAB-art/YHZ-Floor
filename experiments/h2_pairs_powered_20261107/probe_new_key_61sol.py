#!/usr/bin/env python3
"""NON-EVIDENCE probe: does gpt-6.1-sol's backend pool budget-filter the CBC
prompt?  The 5.6-sol pool passes 1/6 at mt=8400 (probe_new_key_series);
if 6.1-sol passes consistently the registered wave could run on it under a
pre-evidence label-switch amendment.  Three calls at 8400 on the frozen
turn-1 prompt bytes.  Key from env only; raw bodies saved."""
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from agentrouter_client import AgentRouterClient, ProviderFailure  # noqa: E402

LABEL = "gpt-6.1-sol"
BASE_URL = "https://agentrouter.org"
TEMP = 1.0
PROMPT_FILE = sorted((HERE / "sessions" / "prompts").glob("*A_INTERACTIVE*seed_441*turn1.txt"))[0]
FROZEN_PROMPT = PROMPT_FILE.read_text()
OUT = HERE / "probe_series_raw"
OUT.mkdir(exist_ok=True)


def main():
    key = os.environ.get("AGENTROUTER_API_KEY")
    if not key:
        sys.exit("AGENTROUTER_API_KEY not in environment")
    client = AgentRouterClient(key, LABEL, BASE_URL, TEMP)
    for i in range(3):
        try:
            resp = client.call(FROZEN_PROMPT, max_tokens=8400, timeout=300)
            meta = resp["metadata"]
            (OUT / f"61sol_{i}_mt8400.json").write_text(resp["raw_body"])
            print(f"{i} 6.1-sol mt=8400: 200 stop={meta['finish_reason']} "
                  f"in={meta['usage'].get('input_tokens')} "
                  f"out={meta['usage'].get('output_tokens')} "
                  f"{meta['elapsed_s']}s head={resp['text'][:70]!r}", flush=True)
        except ProviderFailure as exc:
            print(f"{i} 6.1-sol mt=8400: FAIL category={exc.category} "
                  f"detail={str(exc.detail)[:200]!r}", flush=True)
        time.sleep(5)


if __name__ == "__main__":
    main()
