#!/usr/bin/env python3
"""Diagnostic probe: send the recorded seed-65 prompt and print the gateway's
raw error body (used to explain HTTP 400 before any session is recorded)."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENV = HERE.parents[2] / ".env"


def read_env():
    env = {}
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def main():
    env = read_env()
    prompts = sorted((HERE / "sessions" / "prompts").glob("*seed_65*turn1.txt"))
    if not prompts:
        print("no prompt file")
        return
    prompt = prompts[0].read_text()
    print("prompt_chars", len(prompt), "prompt_sha_prefix", prompts[0].name[:60])
    url = env["AGENTROUTER_BASE_URL"].rstrip("/") + "/v1/messages"
    for model in ("gpt-6.1-sol", "gpt-6-astra", "gpt-5.6-sol"):
        for max_tokens in (4200, 3000, 16000):
            payload = {"model": model, "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}
            request = urllib.request.Request(
                url, data=json.dumps(payload).encode(),
                headers={"content-type": "application/json",
                         "x-api-key": env["AGENTROUTER_API_KEY"],
                         "Authorization": "Bearer " + env["AGENTROUTER_API_KEY"],
                         "anthropic-version": "2023-06-01",
                         "User-Agent": "claude-cli/2.0.0 (external, cli)"})
            try:
                with urllib.request.urlopen(request, timeout=300) as response:
                    body = json.loads(response.read().decode())
                    text = "".join(part.get("text", "")
                                   for part in body.get("content", [])
                                   if part.get("type") == "text")
                    print(model, max_tokens, response.status, "chars", len(text),
                          "stop", body.get("stop_reason"))
                    break
            except urllib.error.HTTPError as exc:
                print(model, max_tokens, exc.code,
                      exc.read().decode()[:400].replace("\n", " "))
            except Exception as exc:  # noqa: BLE001 - diagnostic probe
                print(model, max_tokens, "ERR", type(exc).__name__, str(exc)[:160])


if __name__ == "__main__":
    main()
