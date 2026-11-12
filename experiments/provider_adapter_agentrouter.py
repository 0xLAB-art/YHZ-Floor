#!/usr/bin/env python3
"""AgentRouter transport adapter — second-label cohort (P010L2).

Interface-identical replacement for the frozen APMix adapter in
analysis/checkpoint007_active_experiments/runs_009/provider_adapter.py:
exposes ClaudeProvider (same constructor shape, call(), attest(), model /
endpoint attributes) and ProviderFailure (same categories, same constructor),
so the FROZEN P010 runner binds to this module unmodified via a sys.modules
injection performed by the namespace wrapper. The class name ClaudeProvider is
kept for import compatibility; the transport is AgentRouter.

Disclosed transport differences vs the frozen adapter (all recorded in the
preregistration and per-call request metadata):

  1. Endpoint/model resolved from environment: AGENTROUTER_BASE_URL,
     AGENTROUTER_LABEL_MODEL (default gpt-6.1-sol), AGENTROUTER_API_KEY.
     Credentials are read from the process environment, falling back to the
     gitignored repository-root .env. No key material is ever written into an
     experiment namespace.
  2. User-Agent header `claude-cli/2.0.0 (external, cli)` is REQUIRED by this
     router: an isolated probe (2026-10-25) returned HTTP 401
     UNAUTHENTICATED "unauthorized client detected" for the default
     python-requests UA and for an empty UA, HTTP 200 for the claude-cli UA.
  3. Token floor: the frozen runner requests max_tokens=1400; this adapter
     sends max(requested, LABEL2_TOKEN_FLOOR=2800) uniformly for every cell
     and session. Rationale (measured pre-freeze on a NON-experiment task):
     these labels are reasoning-family — gpt-5.6-sol exhausted 1400 output
     tokens with zero text (stop=length), gpt-6-astra spent 1361, gpt-6.1-sol
     1211. Keeping the frozen 1400 would make truncation (hence terminal
     provider failures) correlate with cell difficulty and fabricate an arm
     difference; the floor removes that artifact channel. Request metadata
     records BOTH max_tokens_requested_by_runner and max_tokens_sent, and the
     raw response is stored verbatim.
  4. Default call timeout 600s (reasoning latency; pre-freeze probe p95 ~160s
     at 1400 tokens). The frozen runner passes no timeout, so this default
     applies.

Everything else — prompt bytes, cell slots, fixture, oracle, policy, feedback
strings, turn flow — comes from the frozen runner untouched.
"""
import hashlib
import json
import os
import time
from pathlib import Path

import requests

LABEL2_TOKEN_FLOOR = 2800
LABEL2_UA = "claude-cli/2.0.0 (external, cli)"
_FROZEN_RUNNER_SHA = "a08eab6f4be2401aacf1b39a47ba6960373164dcc57640d3672d8c36583ee198"


class ProviderFailure(Exception):
    def __init__(self, category, message, response=None):
        super().__init__(message)
        self.category = category
        self.response = response


def _load_env_fallback():
    """Read repo-root .env for AGENTROUTER_* if not already in the environment."""
    root = Path(__file__).resolve().parents[2] / ".env"
    if not root.is_file():
        return
    for line in root.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            k = k.strip()
            if k.startswith("AGENTROUTER_") and k not in os.environ:
                os.environ[k] = v.strip().strip('"').strip("'")


class ClaudeProvider:
    def __init__(self, endpoint=None, model=None, key_path=None):  # noqa: ARG002 (key_path kept for interface parity)
        _load_env_fallback()
        endpoint = endpoint or os.environ.get("AGENTROUTER_BASE_URL")
        self.endpoint = (endpoint or "").rstrip("/")
        if not self.endpoint:
            raise ProviderFailure("CREDENTIAL_MISSING", "AGENTROUTER_BASE_URL is not set")
        self.model = model or os.environ.get("AGENTROUTER_LABEL_MODEL", "gpt-6.1-sol")
        self.key = os.environ.get("AGENTROUTER_API_KEY", "").strip()
        if not self.key:
            raise ProviderFailure("CREDENTIAL_MISSING", "AGENTROUTER_API_KEY is not set")
        if not self.model:
            raise ProviderFailure("CREDENTIAL_EMPTY", "AGENTROUTER_LABEL_MODEL is empty")

    @staticmethod
    def _sha(value):
        return hashlib.sha256(value.encode()).hexdigest()

    def call(self, prompt, max_tokens, timeout=600):
        started = time.time()
        sent_tokens = max(int(max_tokens), LABEL2_TOKEN_FLOOR)
        payload = {"model": self.model, "max_tokens": sent_tokens,
                   "messages": [{"role": "user", "content": prompt}]}
        headers = {"x-api-key": self.key, "Authorization": "Bearer " + self.key,
                   "anthropic-version": "2023-06-01", "content-type": "application/json",
                   "User-Agent": LABEL2_UA}
        request_meta = {"endpoint": self.endpoint + "/v1/messages", "model_requested": self.model,
                        "prompt_sha256": self._sha(prompt), "max_tokens": max_tokens,
                        "max_tokens_requested_by_runner": max_tokens,
                        "max_tokens_sent": sent_tokens,
                        "token_floor_applied": sent_tokens > int(max_tokens),
                        "user_agent": LABEL2_UA,
                        "request_started": started}
        try:
            response = requests.post(request_meta["endpoint"], headers=headers, json=payload, timeout=timeout)
        except requests.Timeout as exc:
            raise ProviderFailure("TIMEOUT", str(exc)) from exc
        except requests.RequestException as exc:
            raise ProviderFailure("PROVIDER_UNAVAILABLE", str(exc)) from exc
        raw = response.content
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderFailure("MALFORMED_PROVIDER_JSON", "provider response was not JSON", response) from exc
        metadata = {
            **request_meta, "http_status": response.status_code,
            "response_headers": {k.lower(): v for k, v in response.headers.items()},
            "response_sha256": hashlib.sha256(raw).hexdigest(), "response_bytes": len(raw),
            "response_finished": time.time(), "provider_object": body.get("object") if isinstance(body, dict) else None,
            "provider_model": body.get("model") if isinstance(body, dict) else None,
            "finish_reason": body.get("stop_reason") if isinstance(body, dict) else None,
            "usage": body.get("usage", {}) if isinstance(body, dict) else {},
        }
        if response.status_code >= 400:
            raise ProviderFailure("HTTP_ERROR", f"HTTP {response.status_code}", response)
        content = body.get("content") if isinstance(body, dict) else None
        text_parts = [x.get("text", "") for x in content or [] if isinstance(x, dict) and x.get("type") == "text"]
        text = "".join(text_parts)
        if not text:
            raise ProviderFailure("EMPTY_RESPONSE", "successful response contained no text", response)
        if metadata["finish_reason"] in ("max_tokens", "length"):
            raise ProviderFailure("INCOMPLETE_RESPONSE", "provider reported truncation", response)
        metadata["output_sha256"] = self._sha(text)
        metadata["output_text"] = text
        return {"metadata": metadata, "body": body, "raw_body": raw.decode("utf-8", "replace"), "text": text}

    def attest(self):
        try:
            r = requests.get(self.endpoint + "/v1/models", headers={"x-api-key": self.key,
                "Authorization": "Bearer " + self.key, "anthropic-version": "2023-06-01",
                "User-Agent": LABEL2_UA}, timeout=30)
        except requests.RequestException as exc:
            return {"status": "PROVIDER_UNAVAILABLE", "error_category": type(exc).__name__}
        try:
            body = r.json()
        except ValueError:
            body = {}
        return {"status": "ATTESTED_METADATA_ONLY" if r.ok else "PROVIDER_REJECTED",
                "http_status": r.status_code,
                "provider_model_ids": [x.get("id") for x in body.get("data", []) if isinstance(x, dict)],
                "endpoint": self.endpoint, "route": self.model}
