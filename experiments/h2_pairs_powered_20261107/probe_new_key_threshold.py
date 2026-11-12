#!/usr/bin/env python3
"""NON-EVIDENCE threshold probe on the NEW operator key (2026-11-07).

Amendment-3.5 methodology, repeated on the replacement key the operator
issued after funding ($125): does the generation-budget content filter
still bind, or was it key-state-dependent?  The frozen CBC turn-1 prompt
bytes (sessions/prompts/...seed_441...turn1.txt) are the stimulus;
max_tokens sweeps the registered probe budgets.  Key read from the
process environment only (AGENTROUTER_API_KEY); never written anywhere.
Prints status + finish reason + usage only."""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from agentrouter_client import AgentRouterClient, ProviderFailure  # noqa: E402

LABEL = "gpt-5.6-sol"
BASE_URL = "https://agentrouter.org"
TEMP = 1.0
PROMPT_FILE = sorted((HERE / "sessions" / "prompts").glob("*A_INTERACTIVE*seed_441*turn1.txt"))[0]
FROZEN_PROMPT = PROMPT_FILE.read_text()
BUDGETS = [32, 8400, 8400, 8400]
SMOKE = "Reply with exactly: OK"


def main():
    key = os.environ.get("AGENTROUTER_API_KEY")
    if not key:
        sys.exit("AGENTROUTER_API_KEY not in environment")
    client = AgentRouterClient(key, LABEL, BASE_URL, TEMP)
    print(f"prompt file: {PROMPT_FILE.name} ({len(FROZEN_PROMPT)} bytes)")
    for label, text, budget in ([("smoke", SMOKE, 16)]
                                + [("cbc", FROZEN_PROMPT, b) for b in BUDGETS]):
        try:
            resp = client.call(text, max_tokens=budget, timeout=300)
            usage = resp.get("usage", {})
            content = resp.get("content") or ""
            print(f"{label} mt={budget}: 200 finish={resp.get('finish_reason')} "
                  f"out={usage.get('output_tokens')} head={content[:60]!r}")
        except ProviderFailure as exc:
            print(f"{label} mt={budget}: PROVIDER_FAILURE "
                  f"category={exc.category} detail={str(exc.detail)[:220]!r}")


if __name__ == "__main__":
    main()
