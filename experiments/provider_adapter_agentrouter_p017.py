#!/usr/bin/env python3
"""AgentRouter transport adapter — P017 (raised token floor).

Interface-identical replacement for the frozen adapter, so the frozen AES-GCM
runner binds to it unmodified through the sys.modules injection the namespace
wrapper performs. Transport, headers, credential resolution, failure categories
and metadata fields are byte-for-byte the same behaviour as
`provider_adapter_agentrouter.py`; exactly ONE constant differs.

## The one change, and where its value comes from

P014 ran with `LABEL2_TOKEN_FLOOR = 2800`. Measured output-token usage over the
63 stored P014 responses:

| start-arm | n | min | median | max |
|---|---|---|---|---|
| C1 (stated, named) | 17 | 512 | 884 | 1264 |
| C3 (withheld, named) | 16 | 690 | 922 | 1764 |
| C2 (withheld, unnamed) | 7 | 2200 | 2573 | 2726 |
| C4 (stated, unnamed) | 23 | 1693 | 2199 | 2747 |

Maximum observed completion: **2747** tokens. Headroom under the old floor:
**53 tokens**. The withheld arms complete at 1.9–3.1x the stated arms, so the old
floor sat on top of the observed distribution — inside the arms under test.

New floor: `round_up(1.5 * 2747, 400) = 4200`.

Rationale, fixed here before P017 runs:
- 1.5x the maximum observed completion, not the mean, because the failure mode is
  the tail (a long reasoning pass that emits no final text), and 19 of 32
  withheld sessions terminated exactly there;
- rounded up to a round hundred so the constant is auditable and not fitted to a
  single observation;
- applied **uniformly to all four cells**, never only to the arms that struggled,
  so a cell cannot be given more room than another and no cell is handed a
  budget advantage that could manufacture an arm difference.

4200 is still far below any provider limit and costs only on the completions that
actually use it (billing is per generated token, not per requested maximum).

Everything else is unchanged: `claude-cli` User-Agent (the route rejects the
default client), x-api-key + Bearer, Anthropic `/v1/messages`, timeout 600 s,
`max_tokens_requested_by_runner` and `max_tokens_sent` both recorded per call,
raw body stored verbatim by the runner. No key material is written to disk.
"""
import hashlib
import json
import os
import time
from pathlib import Path

import requests

# 1.5 x max observed P014 completion (2747), rounded up to a round hundred.
P017_TOKEN_FLOOR = 4200
P017_FLOOR_BASIS = {
    "source_cohort": "P014-INFO-CONTRACT-2X2-AESGCM-NONCE-REUSE-v1",
    "source_max_observed_output_tokens": 2747,
    "previous_floor": 2800,
    "previous_headroom_tokens": 53,
    "rule": "round_up(1.5 * max_observed, 400)",
    "applied_to": "uniformly across C1/C2/C3/C4",
}
P017_UA = "claude-cli/2.0.0 (external, cli)"


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
        try:
            response = requests.post(request_meta["endpoint"], headers=headers,
                                     json=payload, timeout=timeout)
        except requests.Timeout as exc:
            raise ProviderFailure("TIMEOUT", str(exc)) from exc
        except requests.RequestException as exc:
            raise ProviderFailure("PROVIDER_UNAVAILABLE", str(exc)) from exc
        raw = response.content
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderFailure("MALFORMED_PROVIDER_JSON",
                                  "provider response was not JSON", response) from exc
        metadata = {
            **request_meta, "http_status": response.status_code,
            "response_headers": {k.lower(): v for k, v in response.headers.items()},
            "response_sha256": hashlib.sha256(raw).hexdigest(), "response_bytes": len(raw),
            "response_finished": time.time(),
            "provider_object": body.get("object") if isinstance(body, dict) else None,
            "provider_model": body.get("model") if isinstance(body, dict) else None,
            "finish_reason": body.get("stop_reason") if isinstance(body, dict) else None,
            "usage": body.get("usage", {}) if isinstance(body, dict) else {},
        }
        if response.status_code >= 400:
            raise ProviderFailure("HTTP_ERROR", f"HTTP {response.status_code}", response)
        content = body.get("content") if isinstance(body, dict) else None
        text_parts = [x.get("text", "") for x in content or []
                      if isinstance(x, dict) and x.get("type") == "text"]
        text = "".join(text_parts)
        if not text:
            raise ProviderFailure("EMPTY_RESPONSE",
                                  "successful response contained no text", response)
        if metadata["finish_reason"] in ("max_tokens", "length"):
            raise ProviderFailure("INCOMPLETE_RESPONSE",
                                  "provider reported truncation", response)
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
