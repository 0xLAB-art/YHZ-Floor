#!/usr/bin/env python3
"""AgentRouter Responses-API transport client for Amendment-5.

Why this transport exists (measured, see
external_admission_amend4_frontier_20261106/FINDING_TRANSPORT_DECOMPOSITION.md):
the frozen Amendment-4 route served the registered labels through an
Anthropic-messages facade over an OpenAI-chat-style backend
(response ids prefixed `chatcmpl-`). Under that facade, hidden reasoning
consumed the entire completion budget: 220/279 recorded provider responses
ended `stop_reason: "length"` with an EMPTY visible content block while
charging 4200/8400 output tokens (1,323,000 tokens for zero visible text),
and the gateway's `chat-completions` endpoint rejects these models outright
("does not support /v1/chat/completions, please use /v1/responses").

This client therefore speaks the native OpenAI Responses API:
  POST {base}/v1/responses
  body: {model, max_output_tokens, input: <prompt>} — the reasoning.effort
  field is included only when effort is not None (census/calibration
  probes pass effort=None: measured 2026-11-09, the backend ignores the
  field, so evidence calls omit it entirely)
  visible text = first output_text block; usage reports
  output_tokens_details.reasoning_tokens — the previously hidden budget is
  now an exposed, recorded quantity.

Interface-identical to the Amendment-3/4 clients' call site:
  call(prompt, max_tokens) -> {"text", "raw_body", "metadata": {...}}

The API key is read from the process environment by the runner and passed
in; it is never printed and never written to any artifact.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

UA = "claude-cli/2.0.0 (external, cli)"
REASONING_EFFORT = "low"


class ProviderFailure(Exception):
    def __init__(self, category: str, detail: str):
        super().__init__(f"{category}: {detail}")
        self.category = category
        self.detail = detail


class AgentRouterResponsesClient:
    def __init__(self, key: str, model: str, base_url: str,
                 effort: str = REASONING_EFFORT):
        self.key = key
        self.model = model
        self.endpoint = base_url.rstrip("/") + "/v1/responses"
        self.effort = effort

    def call(self, prompt: str, max_output_tokens: int,
             timeout: int = 1800) -> dict:
        body_obj = {
            "model": self.model,
            "max_output_tokens": int(max_output_tokens),
            "input": prompt,
        }
        if self.effort is not None:
            body_obj["reasoning"] = {"effort": self.effort}
        body = json.dumps(body_obj).encode()
        req = urllib.request.Request(
            self.endpoint, data=body,
            headers={"Authorization": "Bearer " + self.key,
                     "content-type": "application/json",
                     "User-Agent": UA})
        t0 = time.time()
        try:
            # Amendment-5 hardening: a slow-drip socket defeats urlopen's
            # per-op timeout (measured 30+ min hangs). Daemon thread + hard
            # 420s join cap bounds every call wall-clock.
            import threading
            _box: dict = {}

            def _go():
                try:
                    with urllib.request.urlopen(req, timeout=timeout) as resp:
                        _box["raw"] = resp.read().decode("utf-8", "replace")
                except Exception as exc:
                    _box["exc"] = exc

            _th = threading.Thread(target=_go, daemon=True)
            _th.start()
            _th.join(1800)
            if _th.is_alive():
                raise TimeoutError("hard 1800s wall-clock cap exceeded")
            if "exc" in _box:
                raise _box["exc"]
            raw = _box["raw"]
        except urllib.error.HTTPError as exc:
            raw_detail = ""
            try:
                raw_detail = exc.read().decode("utf-8", "replace")[:300]
            except Exception:
                pass
            if exc.code in (401, 403):
                raise ProviderFailure("HARNESS_ERROR",
                                      f"HTTP {exc.code}: {raw_detail}")
            if exc.code == 429:
                raise ProviderFailure("RATE_LIMITED", f"HTTP 429: {raw_detail}")
            if exc.code >= 500:
                raise ProviderFailure("SERVER_ERROR",
                                      f"HTTP {exc.code}: {raw_detail}")
            raise ProviderFailure("BAD_RESPONSE",
                                  f"HTTP {exc.code}: {raw_detail}")
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

        text = ""
        for block in data.get("output", []) or []:
            if not isinstance(block, dict) or block.get("type") != "message":
                continue
            for part in block.get("content", []) or []:
                if (isinstance(part, dict)
                        and part.get("type") == "output_text"):
                    text += part.get("text", "") or ""

        usage = data.get("usage") or {}
        details = usage.get("output_tokens_details") or {}
        meta = {
            "finish_reason": data.get("status"),
            "incomplete_reason": (data.get("incomplete_details") or {}).get(
                "reason"),
            "usage": {"input_tokens": usage.get("input_tokens", 0),
                      "output_tokens": usage.get("output_tokens", 0),
                      "reasoning_tokens": details.get("reasoning_tokens", 0)},
            "model_echo": data.get("model"),
            "transport": "responses_api",
            "reasoning_effort": self.effort,
            "elapsed_s": round(time.time() - t0, 2),
        }
        return {"text": text, "raw_body": raw, "metadata": meta}
