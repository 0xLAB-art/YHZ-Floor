#!/usr/bin/env python3
import hashlib
import json
import os
import time
from pathlib import Path

import requests


class ProviderFailure(Exception):
    def __init__(self, category, message, response=None):
        super().__init__(message)
        self.category = category
        self.response = response


class ClaudeProvider:
    def __init__(self, endpoint="https://api.apmix.ai", model="claude-sonnet-4-6-free", key_path=None):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        resolved_key_path = os.environ.get("APMIX_KEY_PATH", key_path)
        if resolved_key_path:
            self.key_path = Path(resolved_key_path)
        else:
            self.key_path = Path.home() / ".config/acts007/apmix.key"
        if not self.key_path.is_file():
            raise ProviderFailure("CREDENTIAL_MISSING", "configured key file is absent: " + str(self.key_path))
        self.key = self.key_path.read_text().strip()
        if not self.key:
            raise ProviderFailure("CREDENTIAL_EMPTY", "configured key file is empty: " + str(self.key_path))

    @staticmethod
    def _sha(value):
        return hashlib.sha256(value.encode()).hexdigest()

    def call(self, prompt, max_tokens, timeout=300):
        started = time.time()
        payload = {"model": self.model, "max_tokens": max_tokens,
                   "messages": [{"role": "user", "content": prompt}]}
        headers = {"x-api-key": self.key, "Authorization": "Bearer " + self.key,
                   "anthropic-version": "2023-06-01", "content-type": "application/json"}
        request_meta = {"endpoint": self.endpoint + "/v1/messages", "model_requested": self.model,
                        "prompt_sha256": self._sha(prompt), "max_tokens": max_tokens,
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
                "Authorization": "Bearer " + self.key, "anthropic-version": "2023-06-01"}, timeout=30)
        except requests.RequestException as exc:
            return {"status": "PROVIDER_UNAVAILABLE", "error_category": type(exc).__name__}
        try:
            body = r.json()
        except ValueError:
            body = {}
        return {"status": "ATTESTED_METADATA_ONLY" if r.ok else "PROVIDER_REJECTED",
                "http_status": r.status_code, "provider_model_ids": [x.get("id") for x in body.get("data", []) if isinstance(x, dict)],
                "endpoint": self.endpoint, "route": self.model}
