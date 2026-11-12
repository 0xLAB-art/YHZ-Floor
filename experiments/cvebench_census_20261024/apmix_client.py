#!/usr/bin/env python3
"""APMIX provider client for cvebench_census_20261024 (CVE-Bench external source census).

Loads provider config from /mnt/nvme5/ACTS-Attack/.env (APMIX_BASE_URL,
APMIX_API_KEY, APMIX_MODEL) at runtime. The key is never printed, never
written into any file under sp2027/, and never included in any persisted
artifact; only hashes and usage counts are recorded.

Call/feedback semantics mirror the retained harness pattern
(run_info_contract_2x2_chacha20.py + runs_009/provider_adapter.py) and the
external_admission_20261024 client, including the /v1 endpoint handling fix
recorded in that namespace's freeze lineage.

Egress guard: requests are restricted to the https://api.apmix.ai provider
endpoint recorded in the approved plan (REMAINING_EXPERIMENTS_PLAN_20261023.md,
Global constraints). Any other scheme or host is rejected before any request
is made; redirects are not followed (requests.post without allow_redirects
keeps the single pinned destination).
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

ENV_PATH = Path("/mnt/nvme5/ACTS-Attack/.env")

ALLOWED_SCHEME = "https"
ALLOWED_HOST = "api.apmix.ai"


def load_env() -> dict:
    cfg = {}
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip()
    return cfg


class ProviderFailure(Exception):
    def __init__(self, category, message, http_status=None):
        super().__init__(message)
        self.category = category
        self.http_status = http_status


def check_egress(url: str) -> None:
    """Reject any destination that is not the pinned provider endpoint."""
    parsed = urlparse(url)
    if parsed.scheme != ALLOWED_SCHEME or parsed.hostname != ALLOWED_HOST:
        raise ProviderFailure(
            "CONFIG_REJECTED",
            f"egress guard: refusing non-pinned endpoint {parsed.scheme}://{parsed.hostname or ''}")


class ApmixClient:
    def __init__(self, env: dict | None = None):
        cfg = env if env is not None else load_env()
        base = cfg["APMIX_BASE_URL"].rstrip("/")
        # The configured base URL already ends in /v1 (Anthropic-compatible root);
        # messages live at <base>/messages, not <base>/v1/messages.
        self.endpoint = base[:-3] if base.endswith("/v1") else base
        self.messages_url = base + "/messages"
        self.models_url = base + "/models"
        self.model = cfg["APMIX_MODEL"]
        self.key = cfg["APMIX_API_KEY"]
        check_egress(self.messages_url)
        check_egress(self.models_url)

    @staticmethod
    def _sha(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def call(self, prompt: str, max_tokens: int, timeout: int = 300) -> dict:
        started = time.time()
        payload = {"model": self.model, "max_tokens": max_tokens,
                   "messages": [{"role": "user", "content": prompt}]}
        headers = {"x-api-key": self.key, "Authorization": "Bearer " + self.key,
                   "anthropic-version": "2023-06-01", "content-type": "application/json"}
        request_meta = {"endpoint": self.messages_url,
                        "model_requested": self.model, "prompt_sha256": self._sha(prompt),
                        "max_tokens": max_tokens, "request_started": started}
        check_egress(request_meta["endpoint"])
        try:
            response = requests.post(request_meta["endpoint"], headers=headers,
                                     json=payload, timeout=timeout, allow_redirects=False)
        except requests.Timeout as exc:
            raise ProviderFailure("TIMEOUT", str(exc)) from exc
        except requests.RequestException as exc:
            raise ProviderFailure("PROVIDER_UNAVAILABLE", str(exc)) from exc
        raw = response.content
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderFailure("MALFORMED_PROVIDER_JSON",
                                  "provider response was not JSON", response.status_code) from exc
        metadata = {**request_meta, "http_status": response.status_code,
                    "response_sha256": hashlib.sha256(raw).hexdigest(),
                    "response_bytes": len(raw), "response_finished": time.time(),
                    "provider_model": body.get("model") if isinstance(body, dict) else None,
                    "finish_reason": body.get("stop_reason") if isinstance(body, dict) else None,
                    "usage": body.get("usage", {}) if isinstance(body, dict) else {}}
        if response.status_code >= 400:
            raise ProviderFailure("HTTP_ERROR", f"HTTP {response.status_code}",
                                  response.status_code)
        content = body.get("content") if isinstance(body, dict) else None
        text = "".join(x.get("text", "") for x in content or []
                       if isinstance(x, dict) and x.get("type") == "text")
        if not text:
            raise ProviderFailure("EMPTY_RESPONSE",
                                  "successful response contained no text", response.status_code)
        if metadata["finish_reason"] in ("max_tokens", "length"):
            raise ProviderFailure("INCOMPLETE_RESPONSE", "provider reported truncation",
                                  response.status_code)
        metadata["output_sha256"] = self._sha(text)
        metadata["output_text"] = text
        return {"metadata": metadata, "raw_body": raw.decode("utf-8", "replace"), "text": text}
