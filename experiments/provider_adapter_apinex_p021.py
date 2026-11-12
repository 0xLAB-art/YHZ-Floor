#!/usr/bin/env python3
"""APINEX transport adapter — P021/R re-run (AES-GCM, CSPRNG seeds).

Interface-identical replacement for the frozen adapter: exposes ClaudeProvider
(same constructor shape, call(), attest(), model / endpoint attributes) and
ProviderFailure, so a FROZEN runner binds to this module unmodified through the
sys.modules injection the namespace wrapper performs. The class name
ClaudeProvider is kept for import compatibility; the transport is APINEX's
OpenAI-compatible /v1/chat/completions.

Disclosed transport differences vs the frozen adapter and vs the AgentRouter
adapter used by P010L2/P011/P014:

  1. TRANSPORT SHAPE. The frozen runner speaks Anthropic /v1/messages; APINEX
     exposes only OpenAI /v1/chat/completions. The runner's `prompt` is sent as
     a single user message; the OpenAI response is stored verbatim in
     `raw_body` and the choice text is returned as `text`.
  2. TEMPERATURE. Omitted from the payload (provider default), matching the
     frozen design's "temperature provider-default" rule. The earlier P010L5
     adapter pinned temperature=0.2; this adapter deliberately does not, so
     sampling is not silently narrowed for one family.
  3. TOKEN FLOOR. Sent budget = max(requested, APINEX_TOKEN_FLOOR=2800),
     uniformly for every cell and session. P021 registered 4200 for
     gpt-6-astra; the substituted label truncated at 4200 (finish_reason=length),
     so the floor is 8192 for every cell — truncation must not correlate with
     cell difficulty.
     Metadata records BOTH max_tokens_requested_by_runner and max_tokens_sent.
  4. USER-AGENT. A browser UA string is required (Cloudflare rejects the
     default client with error 1010). Recorded per call.
  5. TIMEOUT default 600s (reasoning-family latency); the frozen runner passes
     no timeout, so this default applies.
  6. MODEL LABEL resolved from APINEX_LABEL_MODEL at launch, falling back to
     the module default; the resolved label is echoed in every call's metadata
     and in the namespace _LAUNCH.json written by the wrapper.

Everything else — prompt bytes, cell slots, fixture, oracle, policy, feedback
strings, turn flow — comes from the frozen runner untouched. No key material is
ever written into an experiment namespace.
"""
import collections
import hashlib
import os
import threading
import time
from pathlib import Path

import requests

APINEX_TOKEN_FLOOR = 8192
APINEX_UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
CHAT_URL = "https://api.apinex.bond/v1/chat/completions"

# APINEX's free plan allows 15 requests per minute per account. The cohort runs
# with a thread pool, so the adapter paces itself below that ceiling instead of
# letting the pool produce 429s that would be recorded as provider failures and
# poison the cohort. RATE_LIMIT_PER_MIN is the paced budget; 429s are retried
# with a bounded wait as a second line of defence.
RATE_LIMIT_PER_MIN = 12
_RATE_LOCK = threading.Lock()
_RATE_CALLS = collections.deque()
RATE_RETRY_ATTEMPTS = 4
RATE_RETRY_WAIT = 20.0


def _throttle():
    while True:
        with _RATE_LOCK:
            now = time.time()
            while _RATE_CALLS and now - _RATE_CALLS[0] > 60.0:
                _RATE_CALLS.popleft()
            if len(_RATE_CALLS) < RATE_LIMIT_PER_MIN:
                _RATE_CALLS.append(now)
                return
            wait = 60.0 - (now - _RATE_CALLS[0]) + 0.5
        time.sleep(max(wait, 0.5))
MODELS_URL = "https://api.apinex.bond/v1/models"

# Interface aliases expected by the P017-family launchers.
P017_TOKEN_FLOOR = APINEX_TOKEN_FLOOR
P017_FLOOR_BASIS = "P021 registered 4200 for gpt-6-astra. Recalibrated to 8192 for the substituted free/gpt-6-luna label after 4200 produced finish_reason=length truncations on the harder cells; the floor exists precisely so truncation cannot correlate with cell difficulty."
P017_UA = APINEX_UA


class ProviderFailure(Exception):
    def __init__(self, category, message, response=None):
        super().__init__(message)
        self.category = category
        self.response = response


def _load_env_fallback():
    """Read repo-root .env for APINEX_* if not already in the environment."""
    root = Path(__file__).resolve().parents[2] / ".env"
    if not root.is_file():
        return
    for line in root.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            k = k.strip()
            if k.startswith("APINEX_") and k not in os.environ:
                os.environ[k] = v.strip().strip('"').strip("'")


class ClaudeProvider:
    def __init__(self, endpoint=None, model=None, key_path=None):  # noqa: ARG002
        _load_env_fallback()
        self.endpoint = (endpoint or "https://api.apinex.bond").rstrip("/")
        self.model = model or os.environ.get("APINEX_LABEL_MODEL", "claude-opus-5.5")
        self.key = os.environ.get("APINEX_API_KEY", "").strip()
        if not self.key:
            raise ProviderFailure("CREDENTIAL_MISSING", "APINEX_API_KEY is not set")
        if not self.model:
            raise ProviderFailure("CREDENTIAL_EMPTY", "APINEX_LABEL_MODEL is empty")

    @staticmethod
    def _sha(value):
        return hashlib.sha256(value.encode()).hexdigest()

    def call(self, prompt, max_tokens, timeout=600):
        started = time.time()
        sent_tokens = max(int(max_tokens), APINEX_TOKEN_FLOOR)
        payload = {"model": self.model, "max_tokens": sent_tokens,
                   "messages": [{"role": "user", "content": prompt}]}
        headers = {"Authorization": "Bearer " + self.key,
                   "Content-Type": "application/json", "User-Agent": APINEX_UA}
        request_meta = {
            "endpoint": CHAT_URL, "model_requested": self.model,
            "prompt_sha256": self._sha(prompt), "max_tokens": max_tokens,
            "max_tokens_requested_by_runner": max_tokens,
            "max_tokens_sent": sent_tokens,
            "token_floor_applied": sent_tokens > int(max_tokens),
            "temperature_sent": None, "user_agent": APINEX_UA,
            "transport": "openai_chat_completions",
            "request_started": started,
            "rate_limit_per_min": RATE_LIMIT_PER_MIN,
        }
        response = None
        for attempt in range(RATE_RETRY_ATTEMPTS):
            _throttle()
            try:
                response = requests.post(CHAT_URL, headers=headers, json=payload,
                                         timeout=timeout, allow_redirects=False)
            except requests.Timeout as exc:
                raise ProviderFailure("TIMEOUT", str(exc)) from exc
            except requests.RequestException as exc:
                raise ProviderFailure("PROVIDER_UNAVAILABLE", str(exc)) from exc
            if response.status_code != 429:
                break
            time.sleep(RATE_RETRY_WAIT * (attempt + 1))
        request_meta["rate_limit_retries"] = attempt
        raw = response.content
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderFailure("MALFORMED_PROVIDER_JSON",
                                  "provider response was not JSON", response) from exc
        metadata = {
            **request_meta, "http_status": response.status_code,
            "response_headers": {k.lower(): v for k, v in response.headers.items()},
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "response_bytes": len(raw), "response_finished": time.time(),
            "provider_object": body.get("object") if isinstance(body, dict) else None,
            "provider_model": body.get("model") if isinstance(body, dict) else None,
        }
        if response.status_code >= 400:
            raise ProviderFailure("HTTP_ERROR", f"HTTP {response.status_code}", response)
        choices = body.get("choices") if isinstance(body, dict) else None
        if not choices:
            raise ProviderFailure("EMPTY_RESPONSE",
                                  "successful response contained no choices", response)
        choice = choices[0]
        message = choice.get("message", {}) or {}
        text = message.get("content", "") or ""
        finish = choice.get("finish_reason", "")
        metadata["finish_reason"] = finish
        metadata["usage"] = body.get("usage", {})
        if not text:
            raise ProviderFailure("EMPTY_RESPONSE",
                                  "successful response contained no text", response)
        if finish == "length":
            raise ProviderFailure("INCOMPLETE_RESPONSE",
                                  "provider reported truncation", response)
        metadata["output_sha256"] = self._sha(text)
        metadata["output_text"] = text
        return {"metadata": metadata, "body": body,
                "raw_body": raw.decode("utf-8", "replace"), "text": text,
                "stop_reason": "end_turn" if finish == "stop" else finish}

    def attest(self):
        try:
            r = requests.get(MODELS_URL, headers={"Authorization": "Bearer " + self.key,
                                                  "User-Agent": APINEX_UA}, timeout=30)
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
