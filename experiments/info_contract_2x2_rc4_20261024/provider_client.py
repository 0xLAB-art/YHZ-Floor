"""APMix Anthropic-compatible provider client for P011-INFO-CONTRACT-2X2-RC4-v1.

Reads APMIX_BASE_URL / APMIX_API_KEY / APMIX_MODEL from the repo-root `.env`
(process environment takes precedence). The API key is held in memory only:
it is never printed, never logged, and never written into any file under
sp2027/. Interface mirrors the retained P009/P010 provider adapter
(call / attest / ProviderFailure categories) so the runner is a structural
mirror of the P010 protocol.
"""
import hashlib
import os
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[3]  # namespace -> research_execution -> sp2027 -> repo root


def load_env(path=None):
    """Parse a KEY=VALUE .env file; comments and blank lines ignored."""
    env = {}
    p = Path(path) if path else REPO_ROOT / ".env"
    if p.is_file():
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


class ProviderFailure(Exception):
    def __init__(self, category, message, response=None):
        super().__init__(message)
        self.category = category
        self.response = response


class ClaudeProvider:
    def __init__(self):
        env = load_env()
        self.endpoint = (os.environ.get("APMIX_BASE_URL") or env.get("APMIX_BASE_URL") or "").rstrip("/")
        self.model = os.environ.get("APMIX_MODEL") or env.get("APMIX_MODEL") or "claude-sonnet-4-6-free"
        self.key = os.environ.get("APMIX_API_KEY") or env.get("APMIX_API_KEY") or ""
        if not self.endpoint:
            raise ProviderFailure("CREDENTIAL_MISSING", "APMIX_BASE_URL is not configured")
        if not self.key:
            raise ProviderFailure("CREDENTIAL_MISSING", "APMIX_API_KEY is not configured")
        if self.endpoint.endswith("/v1"):
            self.messages_url = self.endpoint + "/messages"
            self.models_url = self.endpoint + "/models"
        else:
            self.messages_url = self.endpoint + "/v1/messages"
            self.models_url = self.endpoint + "/v1/models"

    @staticmethod
    def _sha(value):
        return hashlib.sha256(value.encode()).hexdigest()

    def _headers(self):
        return {"x-api-key": self.key, "Authorization": "Bearer " + self.key,
                "anthropic-version": "2023-06-01", "content-type": "application/json"}

    def call(self, prompt, max_tokens, timeout=300):
        started = time.time()
        payload = {"model": self.model, "max_tokens": max_tokens,
                   "messages": [{"role": "user", "content": prompt}]}
        request_meta = {"endpoint": self.messages_url, "model_requested": self.model,
                        "prompt_sha256": self._sha(prompt), "max_tokens": max_tokens,
                        "request_started": started}
        try:
            response = requests.post(self.messages_url, headers=self._headers(),
                                     json=payload, timeout=timeout)
        except requests.Timeout as exc:
            raise ProviderFailure("TIMEOUT", str(exc)) from exc
        except requests.RequestException as exc:
            raise ProviderFailure("PROVIDER_UNAVAILABLE", type(exc).__name__ + ": " + str(exc)) from exc
        raw = response.content
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderFailure("MALFORMED_PROVIDER_JSON", "provider response was not JSON", response) from exc
        metadata = {
            **request_meta, "http_status": response.status_code,
            "response_headers": {k.lower(): v for k, v in response.headers.items()
                                 if k.lower() not in ("set-cookie",)},
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
        text = "".join(x.get("text", "") for x in content or []
                       if isinstance(x, dict) and x.get("type") == "text")
        if not text:
            raise ProviderFailure("EMPTY_RESPONSE", "successful response contained no text", response)
        if metadata["finish_reason"] in ("max_tokens", "length"):
            raise ProviderFailure("INCOMPLETE_RESPONSE", "provider reported truncation", response)
        metadata["output_sha256"] = self._sha(text)
        return {"metadata": metadata, "body": body,
                "raw_body": raw.decode("utf-8", "replace"), "text": text}

    def attest(self):
        try:
            r = requests.get(self.models_url, headers=self._headers(), timeout=30)
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
