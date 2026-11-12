#!/usr/bin/env python3
"""AgentRouter transport client for Amendment-4 (frontier label panel).

Anthropic-messages transport per the frozen project adapters
(provider_adapter_agentrouter_p017.py): POST {base}/v1/messages with
x-api-key + Bearer + anthropic-version 2023-06-01 and the claude-cli
User-Agent the route requires.  Interface-identical to the Amendment-3
ApinexClient call site: call(prompt, max_tokens) -> {"text", "raw_body",
"metadata": {"finish_reason", "usage"}}.

The API key is read from the process environment by the runner and passed
in; it is never printed and never written to any artifact.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

UA = "claude-cli/2.0.0 (external, cli)"
ANTHROPIC_VERSION = "2023-06-01"


class ProviderFailure(Exception):
    def __init__(self, category: str, detail: str):
        super().__init__(f"{category}: {detail}")
        self.category = category
        self.detail = detail


class AgentRouterClient:
    def __init__(self, key: str, model: str, base_url: str, temperature: float):
        self.key = key
        self.model = model
        self.endpoint = base_url.rstrip("/") + "/v1/messages"
        self.temperature = temperature

    def call(self, prompt: str, max_tokens: int, timeout: int = 600) -> dict:
        body_obj = {
            "model": self.model,
            "max_tokens": int(max_tokens),
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.temperature is not None:
            body_obj["temperature"] = self.temperature
        body = json.dumps(body_obj).encode()
        req = urllib.request.Request(
            self.endpoint, data=body,
            headers={"x-api-key": self.key,
                     "Authorization": "Bearer " + self.key,
                     "anthropic-version": ANTHROPIC_VERSION,
                     "content-type": "application/json",
                     "User-Agent": UA})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8", "replace")[:300]
            except Exception:
                pass
            if exc.code in (401, 403):
                raise ProviderFailure("HARNESS_ERROR",
                                      f"HTTP {exc.code}: {detail}")
            if exc.code == 429:
                raise ProviderFailure("RATE_LIMITED", f"HTTP 429: {detail}")
            if exc.code >= 500:
                raise ProviderFailure("SERVER_ERROR", f"HTTP {exc.code}: {detail}")
            raise ProviderFailure("BAD_RESPONSE", f"HTTP {exc.code}: {detail}")
        except urllib.error.URLError as exc:
            raise ProviderFailure("TIMEOUT", f"URLError: {exc}")
        except TimeoutError:
            raise ProviderFailure("TIMEOUT", "request timeout")
        except Exception as exc:
            raise ProviderFailure("BAD_RESPONSE", f"{type(exc).__name__}: {exc}")

        try:
            data = json.loads(raw)
        except ValueError as exc:
            raise ProviderFailure("BAD_RESPONSE", f"non-JSON body: {exc}")
        text = "".join(block.get("text", "") for block in data.get("content", [])
                       if isinstance(block, dict) and block.get("type") == "text")
        meta = {"finish_reason": data.get("stop_reason"),
                "usage": data.get("usage") or {},
                "model_echo": data.get("model"),
                "elapsed_s": round(time.time() - t0, 2)}
        return {"text": text, "raw_body": raw, "metadata": meta}
