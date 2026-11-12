#!/usr/bin/env python3
"""APINEX OpenAI-compatible client — Amendment 3 (frozen route).

The key is read by the runner from the process environment (APINEX_API_KEY)
and is never printed or written to any sp2027 artifact.  The client implements
only the transport + response parsing; retry policy lives in the runner
(two-sided provider-failure rule).
"""
from __future__ import annotations

import hashlib
import json
import time

import requests


class ProviderFailure(Exception):
    def __init__(self, category, message, http_status=None):
        super().__init__(message)
        self.category = category
        self.http_status = http_status


class ApinexClient:
    def __init__(self, key: str, model: str,
                 base_url: str = "https://api.apinex.bond",
                 temperature: float = 0.2):
        self.endpoint = base_url.rstrip("/")
        self.url = self.endpoint + "/v1/chat/completions"
        self.model = model
        self.key = key
        self.temperature = temperature

    @staticmethod
    def _sha(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def call(self, prompt: str, max_tokens: int, timeout: int = 300) -> dict:
        started = time.time()
        payload = {
            "model": self.model,
            "max_tokens": int(max_tokens),
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {"Authorization": "Bearer " + self.key,
                   "Content-Type": "application/json"}
        request_meta = {"endpoint": self.url, "model_requested": self.model,
                        "prompt_sha256": self._sha(prompt),
                        "max_tokens": int(max_tokens),
                        "temperature": self.temperature,
                        "request_started": started}
        try:
            response = requests.post(self.url, headers=headers, json=payload,
                                     timeout=timeout)
        except requests.Timeout as exc:
            raise ProviderFailure("TIMEOUT", str(exc)) from exc
        except requests.RequestException as exc:
            raise ProviderFailure("PROVIDER_UNAVAILABLE", str(exc)) from exc
        raw = response.content
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderFailure("MALFORMED_PROVIDER_JSON",
                                  "provider response was not JSON",
                                  response.status_code) from exc
        usage = body.get("usage") or {} if isinstance(body, dict) else {}
        metadata = {
            **request_meta,
            "http_status": response.status_code,
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "response_bytes": len(raw),
            "response_finished": time.time(),
            "provider_model": body.get("model") if isinstance(body, dict) else None,
            "usage": usage,
        }
        if response.status_code in (401, 402, 403):
            raise ProviderFailure("HARNESS_ERROR",
                                  f"provider auth/billing error HTTP {response.status_code}",
                                  response.status_code)
        if response.status_code == 429 or response.status_code >= 500:
            raise ProviderFailure("PROVIDER_UNAVAILABLE",
                                  f"provider transient error HTTP {response.status_code}",
                                  response.status_code)
        if response.status_code >= 400:
            raise ProviderFailure("HTTP_ERROR",
                                  f"HTTP {response.status_code}",
                                  response.status_code)
        choices = body.get("choices") if isinstance(body, dict) else None
        if not choices:
            raise ProviderFailure("EMPTY_RESPONSE",
                                  "response contained no choices",
                                  response.status_code)
        first = choices[0] if isinstance(choices[0], dict) else {}
        message = first.get("message") if isinstance(first.get("message"), dict) else {}
        text = message.get("content") or ""
        if not text:
            raise ProviderFailure("EMPTY_RESPONSE",
                                  "response contained no text",
                                  response.status_code)
        metadata["finish_reason"] = first.get("finish_reason")
        metadata["output_sha256"] = self._sha(text)
        metadata["output_text"] = text
        return {"metadata": metadata, "raw_body": raw.decode("utf-8", "replace"),
                "text": text}
