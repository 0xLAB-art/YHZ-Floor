#!/usr/bin/env python3
"""Bounded model client for the Stage 3 untrusted submitter.

Exact approved route only: one request per submission, no retry, no fallback
model, no seed replacement.  The API key is read from the environment and is
never written to an artifact.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any

import requests

APPROVED_ENDPOINT = "https://api.apmix.ai"
APPROVED_MODEL = "claude-sonnet-4-6-free"
MAX_TOKENS = 8000
TIMEOUT_SECONDS = 300

_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


@dataclass(frozen=True)
class ModelReply:
    """One provider response and its recorded provenance."""

    text: str
    http_status: int
    provider_model: str
    usage: dict[str, Any]
    prompt_sha256: str
    response_sha256: str
    elapsed_seconds: float
    call_index: int


class ModelUnavailable(RuntimeError):
    """The approved route did not return usable text."""


def credential_from_environment() -> str:
    key = os.environ.get("APMIX_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ModelUnavailable("APMIX_API_KEY is not exported")
    return key


def extract_json_object(text: str) -> dict[str, Any] | None:
    """Parse the first JSON object in a model response, if there is one."""
    match = _JSON_OBJECT.search(text)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except ValueError:
        return None
    return parsed if isinstance(parsed, dict) else None


def call_model(prompt: str, api_key: str, call_index: int) -> ModelReply:
    """Make one request on the approved route."""
    payload = {
        "model": APPROVED_MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "x-api-key": api_key,
        "Authorization": "Bearer " + api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    started = time.time()
    response = requests.post(
        APPROVED_ENDPOINT + "/v1/messages",
        headers=headers,
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )
    elapsed = time.time() - started
    if response.status_code != 200:
        raise ModelUnavailable(f"HTTP {response.status_code}")
    body = response.json()
    text = "".join(
        block.get("text", "")
        for block in body.get("content", [])
        if isinstance(block, dict) and block.get("type") == "text"
    )
    if not text:
        raise ModelUnavailable("provider returned no text")
    return ModelReply(
        text=text,
        http_status=response.status_code,
        provider_model=str(body.get("model")),
        usage=body.get("usage", {}),
        prompt_sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        response_sha256=hashlib.sha256(response.content).hexdigest(),
        elapsed_seconds=round(elapsed, 6),
        call_index=call_index,
    )