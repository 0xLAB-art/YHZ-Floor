#!/usr/bin/env python3
"""APINEX transport adapter for P010L5 (fifth-label replication).

Exposes ClaudeProvider (same interface as the frozen adapter) so the frozen
runner binds it via sys.modules injection. Translates the frozen runner's
Anthropic-format interface to APINEX's OpenAI-compatible /v1/chat/completions.
The raw OpenAI response is stored in raw_body for the fingerprint audit.

Endpoints are hardcoded constants (no dynamic URL construction):
- Chat: https://api.apinex.bond/v1/chat/completions
- Models: https://api.apinex.bond/v1/models
- User-Agent: Mozilla/5.0 (required by Cloudflare, error 1010 otherwise)
"""
import hashlib, json, os, time
from pathlib import Path
import requests

_UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"

class ProviderFailure(Exception):
    def __init__(self, category, message, response=None):
        super().__init__(message)
        self.category = category
        self.response = response

class ClaudeProvider:
    def __init__(self, endpoint=None, model=None, key_path=None):
        self.endpoint = "https://api.apinex.bond"
        self.model = model or os.environ.get("APINEX_LABEL_MODEL", "free/kimi-k3")
        env_path = Path(__file__).resolve().parents[2] / ".env"
        env = {}
        if env_path.is_file():
            for line in env_path.read_text().splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    env.setdefault(k.strip(), v.strip())
        self.key = (os.environ.get("APINEX_API_KEY") or
                    env.get("APINEX_API_KEY", "")).strip()
        if not self.key:
            raise ProviderFailure("CREDENTIAL_EMPTY", "APINEX_API_KEY is empty")

    @staticmethod
    def _sha(value):
        return hashlib.sha256(value.encode()).hexdigest()

    def call(self, prompt, max_tokens, timeout=300):
        started = time.time()
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "User-Agent": _UA,
        }
        request_meta = {
            "endpoint": "https://api.apinex.bond/v1/chat/completions",
            "model_requested": self.model,
            "prompt_sha256": self._sha(prompt),
            "max_tokens": max_tokens,
            "request_started": started,
        }
        try:
            response = requests.post(
                "https://api.apinex.bond/v1/chat/completions",
                headers=headers, json=payload, timeout=timeout,
                allow_redirects=False,
            )
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
            **request_meta,
            "http_status": response.status_code,
            "response_headers": {k.lower(): v for k, v in response.headers.items()},
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "response_bytes": len(raw),
            "response_finished": time.time(),
            "provider_model": body.get("model") if isinstance(body, dict) else None,
            "provider_object": body.get("object") if isinstance(body, dict) else None,
        }
        if response.status_code >= 400:
            raise ProviderFailure("HTTP_ERROR",
                                  f"HTTP {response.status_code}", response)
        choices = body.get("choices") if isinstance(body, dict) else None
        if not choices:
            raise ProviderFailure("EMPTY_RESPONSE",
                                  "successful response contained no choices", response)
        choice = choices[0]
        message = choice.get("message", {})
        text = message.get("content", "")
        finish = choice.get("finish_reason", "")
        metadata["finish_reason"] = finish
        metadata["usage"] = body.get("usage", {})
        metadata["output_sha256"] = self._sha(text)
        metadata["output_text"] = text
        if not text:
            raise ProviderFailure("EMPTY_RESPONSE",
                                  "successful response contained no text", response)
        if finish in ("length",):
            raise ProviderFailure("INCOMPLETE_RESPONSE",
                                  "provider reported truncation", response)
        return {
            "metadata": metadata, "body": body,
            "raw_body": raw.decode("utf-8", "replace"),
            "text": text,
            "stop_reason": "end_turn" if finish == "stop" else finish,
        }

    def attest(self):
        try:
            r = requests.get(
                "https://api.apinex.bond/v1/models",
                headers={"Authorization": "Bearer " + self.key}, timeout=30)
        except requests.RequestException as exc:
            return {"status": "PROVIDER_UNAVAILABLE",
                    "error_category": type(exc).__name__}
        try:
            body = r.json()
        except ValueError:
            body = {}
        return {
            "status": "ATTESTED_METADATA_ONLY" if r.ok else "PROVIDER_REJECTED",
            "http_status": r.status_code,
            "provider_model_ids": [x.get("id") for x in body.get("data", [])
                                   if isinstance(x, dict)],
            "endpoint": self.endpoint, "route": self.model,
        }
