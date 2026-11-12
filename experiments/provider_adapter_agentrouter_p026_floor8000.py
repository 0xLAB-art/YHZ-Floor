#!/usr/bin/env python3
"""AgentRouter transport adapter — P017 token floor + P023 transport retry.

Interface-identical to `provider_adapter_agentrouter_p017.py` except for one
added layer, declared in the P023 preregistration before the first call.

## Why P023 exists

P021 lost 226 of 384 sessions to provider-level failures (189 HTTP_ERROR, 35
EMPTY_RESPONSE, 2 TIMEOUT) on an otherwise live route. The same endpoint
answered 200 in ~4 s between failure bursts, and the failures arrived a median
2.25 s after the request started (56 of 226 in under 2 s). The P017 adapter
recorded only the failure *category*, so the HTTP status and body that would
identify the cause were discarded. P023 adds two things and changes nothing the
model sees: (a) transport retry, (b) failure forensics.

## What is retried — transport only

Only failures where NO completion was delivered:

  * connection errors and timeouts,
  * HTTP 408, 409, 425, 429, any 5xx, and 52x,
  * HTTP 200 whose body is not JSON (nothing usable was delivered).

At most `P023_MAX_ATTEMPTS` attempts per call, fixed 2/5/12 s backoff, no
jitter, so the retry sequence is auditable from the log.

## What is NOT retried — model-level outcomes

`EMPTY_RESPONSE` (a completion WAS generated but contained no text block),
`INCOMPLETE_RESPONSE` (provider-reported max_tokens), non-retryable 4xx, and
every oracle/parse outcome stay terminal per session exactly as in P014-P022.
Retrying them would resample the model, not repair transport.

Everything else is P017 behaviour unchanged: `claude-cli` User-Agent,
x-api-key + Bearer, Anthropic `/v1/messages`, 600 s timeout, token floor 4200,
per-call metadata, raw body stored verbatim by the runner. No key material is
written to disk.
"""
import hashlib
import json
import os
import time
from pathlib import Path

import requests

# 1.5 x max observed P014 completion (2747), rounded up to a round hundred.
P017_TOKEN_FLOOR = 8000  # P026 floor-sensitivity registration: raised from 4200 (see PREREGISTRATION.md)
P017_FLOOR_BASIS = {
    "source_cohort": "P014-INFO-CONTRACT-2X2-AESGCM-NONCE-REUSE-v1",
    "source_max_observed_output_tokens": 2747,
    "previous_floor": 2800,
    "previous_headroom_tokens": 53,
    "rule": "round_up(1.5 * max_observed, 400)",
    "applied_to": "uniformly across C1/C2/C3/C4",
}
P017_UA = "claude-cli/2.0.0 (external, cli)"

# --- P023 transport-retry policy (registered before the first provider call) ---
P023_MAX_ATTEMPTS = 4
P023_BACKOFF_SECONDS = (2, 5, 12)
P023_RETRY_STATUS = frozenset({408, 409, 425, 429, 500, 501, 502, 503, 504,
                               520, 521, 522, 523, 524, 529})
# Router-side defect observed live on 2026-11-03: a 400 whose body reports that
# `stream_options` was set without `stream`. This adapter never sends either
# parameter, so the router is rejecting its own injection before any generation.
# Such a 400 is retried as transport; every other 400 stays a client error.
P023_RETRY_BODY_MARKERS = ("stream_options",)
P023_POLICY = {
    "max_attempts_per_call": P023_MAX_ATTEMPTS,
    "backoff_seconds": list(P023_BACKOFF_SECONDS),
    "jitter": False,
    "retry_status": sorted(P023_RETRY_STATUS),
    "retry_body_markers": list(P023_RETRY_BODY_MARKERS),
    "retried_classes": ["TIMEOUT", "PROVIDER_UNAVAILABLE", "MALFORMED_PROVIDER_JSON",
                        "HTTP_ERROR with retry_status",
                        "HTTP 400 carrying a retry_body_marker"],
    "never_retried": ["EMPTY_RESPONSE", "INCOMPLETE_RESPONSE",
                      "HTTP_ERROR outside retry_status", "CREDENTIAL_MISSING",
                      "CREDENTIAL_EMPTY"],
}


def _failure_log(payload):
    """Append one JSON line per failed attempt when ACTS_FAILURE_LOG is set."""
    path = os.environ.get("ACTS_FAILURE_LOG")
    if not path:
        return
    try:
        with open(path, "a") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
    except OSError:
        pass


class ProviderFailure(Exception):
    def __init__(self, category, message, response=None, retryable=False,
                 http_status=None, body_excerpt=None):
        super().__init__(message)
        self.category = category
        self.response = response
        self.retryable = retryable
        self.http_status = http_status
        self.body_excerpt = body_excerpt


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
    def __init__(self, endpoint=None, model=None, key_path=None):  # noqa: ARG002
        _load_env_fallback()
        endpoint = endpoint or os.environ.get("AGENTROUTER_BASE_URL")
        self.endpoint = (endpoint or "").rstrip("/")
        if not self.endpoint:
            raise ProviderFailure("CREDENTIAL_MISSING", "AGENTROUTER_BASE_URL is not set")
        self.model = model or os.environ.get("AGENTROUTER_LABEL_MODEL", "gpt-6-astra")
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
        sent_tokens = max(int(max_tokens), P017_TOKEN_FLOOR)
        payload = {"model": self.model, "max_tokens": sent_tokens,
                   "messages": [{"role": "user", "content": prompt}]}
        headers = {"x-api-key": self.key, "Authorization": "Bearer " + self.key,
                   "anthropic-version": "2023-06-01", "content-type": "application/json",
                   "User-Agent": P017_UA}
        request_meta = {"endpoint": self.endpoint + "/v1/messages",
                        "model_requested": self.model,
                        "prompt_sha256": self._sha(prompt), "max_tokens": max_tokens,
                        "max_tokens_requested_by_runner": max_tokens,
                        "max_tokens_sent": sent_tokens,
                        "token_floor_applied": sent_tokens > int(max_tokens),
                        "token_floor_value": P017_TOKEN_FLOOR,
                        "user_agent": P017_UA,
                        "request_started": started}
        last = None
        for attempt in range(1, P023_MAX_ATTEMPTS + 1):
            try:
                return self._attempt(request_meta, headers, payload, timeout, attempt)
            except ProviderFailure as exc:
                last = exc
                _failure_log({"attempt": attempt,
                              "category": exc.category,
                              "http_status": exc.http_status,
                              "message": str(exc)[:400],
                              "body_excerpt": exc.body_excerpt,
                              "retryable": exc.retryable,
                              "max_attempts": P023_MAX_ATTEMPTS,
                              "endpoint": request_meta["endpoint"],
                              "time": time.time()})
                if not exc.retryable or attempt == P023_MAX_ATTEMPTS:
                    raise
                time.sleep(P023_BACKOFF_SECONDS[min(attempt - 1,
                                                    len(P023_BACKOFF_SECONDS) - 1)])
        raise last

    def _attempt(self, request_meta, headers, payload, timeout, attempt):
        try:
            response = requests.post(request_meta["endpoint"], headers=headers,
                                     json=payload, timeout=timeout)
        except requests.Timeout as exc:
            raise ProviderFailure("TIMEOUT", str(exc), retryable=True) from exc
        except requests.RequestException as exc:
            raise ProviderFailure("PROVIDER_UNAVAILABLE", str(exc), retryable=True) from exc
        raw = response.content
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderFailure("MALFORMED_PROVIDER_JSON",
                                  "provider response was not JSON", response,
                                  retryable=True,
                                  http_status=response.status_code,
                                  body_excerpt=raw[:400].decode("utf-8", "replace")) from exc
        metadata = {
            **request_meta, "http_status": response.status_code,
            "response_headers": {k.lower(): v for k, v in response.headers.items()},
            "response_sha256": hashlib.sha256(raw).hexdigest(), "response_bytes": len(raw),
            "response_finished": time.time(),
            "provider_object": body.get("object") if isinstance(body, dict) else None,
            "provider_model": body.get("model") if isinstance(body, dict) else None,
            "finish_reason": body.get("stop_reason") if isinstance(body, dict) else None,
            "usage": body.get("usage", {}) if isinstance(body, dict) else {},
            "p023_attempt": attempt,
            "p023_transport_policy": P023_POLICY,
        }
        if response.status_code >= 400:
            excerpt = raw[:400].decode("utf-8", "replace")
            retryable = (response.status_code in P023_RETRY_STATUS or
                         any(m in excerpt for m in P023_RETRY_BODY_MARKERS))
            raise ProviderFailure("HTTP_ERROR", f"HTTP {response.status_code}", response,
                                  retryable=retryable,
                                  http_status=response.status_code,
                                  body_excerpt=excerpt)
        content = body.get("content") if isinstance(body, dict) else None
        text_parts = [x.get("text", "") for x in content or []
                      if isinstance(x, dict) and x.get("type") == "text"]
        text = "".join(text_parts)
        if not text:
            raise ProviderFailure("EMPTY_RESPONSE",
                                  "successful response contained no text", response,
                                  retryable=False,
                                  http_status=response.status_code,
                                  body_excerpt=raw[:400].decode("utf-8", "replace"))
        if metadata["finish_reason"] in ("max_tokens", "length"):
            raise ProviderFailure("INCOMPLETE_RESPONSE",
                                  "provider reported truncation", response,
                                  retryable=False,
                                  http_status=response.status_code)
        metadata["output_sha256"] = self._sha(text)
        metadata["output_text"] = text
        return {"metadata": metadata, "body": body,
                "raw_body": raw.decode("utf-8", "replace"), "text": text}

    def attest(self):
        try:
            r = requests.get(self.endpoint + "/v1/models",
                             headers={"x-api-key": self.key,
                                      "Authorization": "Bearer " + self.key,
                                      "anthropic-version": "2023-06-01",
                                      "User-Agent": P017_UA}, timeout=30)
        except requests.RequestException as exc:
            return {"status": "PROVIDER_UNAVAILABLE",
                    "error_category": type(exc).__name__}
        try:
            body = r.json()
        except ValueError:
            body = {}
        return {"status": "ATTESTED_METADATA_ONLY" if r.ok else "PROVIDER_REJECTED",
                "http_status": r.status_code,
                "provider_model_ids": [x.get("id") for x in body.get("data", [])
                                       if isinstance(x, dict)],
                "endpoint": self.endpoint, "route": self.model}
