#!/usr/bin/env python3
"""Independent cryptographic reference verifier for Stage 1 (TOEEA-1).

This component plays the role that the historical
``contract_sound_stage01_reference_verifier_v2.py`` played, but it adds two
things the historical component does not have:

  1. it runs as a *separate party* that holds a secret Ed25519 key, so the
     verdict is not forgeable by the artifact producer; and
  2. it explicitly BINDS the verdict to the digest of the candidate bytes it
     actually read and to the digest of the private target state it actually
     read, so a later consumer can join the verdict to a specific artifact.

The cryptographic predicate itself is NOT re-implemented: it is obtained by
importing the frozen historical reference verifier and calling its
``ecdsa_valid`` / ``chacha_valid`` functions.  Any difference between Stage 1
and the historical path is therefore attributable to evidence binding, not to
a different mathematical definition of the predicate.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from s1_common import (
    KIND_REFERENCE_VERDICT,
    ROLE_REFERENCE_VERIFIER,
    SIGNING_CONTEXT,
    build_context,
    issuer_policy,
    load_ed25519_private_key,
    load_frozen_reference_verifier,
    sha256_bytes,
    sha256_file,
    sign_context_bytes,
)

VERIFIER_VERSION = "acts-s1-reference-verifier/1"


class ReferenceVerifier:
    """Computes the cryptographic predicate and signs a bound verdict."""

    def __init__(self, key_path: Path) -> None:
        self.key_path = Path(key_path)
        self._private_key = load_ed25519_private_key(self.key_path)
        self._frozen = load_frozen_reference_verifier()

    def evaluate(
        self,
        *,
        target_state_path: Path,
        stdout_path: Path,
        attempt_id: str,
        epoch: int,
        target_id: str,
        session_id: str,
    ) -> dict[str, Any]:
        """Evaluate the candidate captured in ``stdout_path``.

        The reference verifier consumes the *captured stdout* (whose digest the
        trusted execution observer signs) and applies exactly the historical
        ``json-last-line-v1`` parse before running the frozen predicate.  It
        therefore never depends on an unreferenced output file that anybody
        could have written after the fact.
        """
        target_state_path = Path(target_state_path)
        stdout_path = Path(stdout_path)

        target_sha = sha256_file(target_state_path)
        stdout_sha = sha256_file(stdout_path)
        target = json.loads(target_state_path.read_text())

        candidate_parse_ok = True
        candidate: Any = None
        evaluated_bytes = b""
        try:
            text = stdout_path.read_bytes().decode("utf-8", errors="replace")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if lines:
                evaluated_bytes = lines[-1].encode("utf-8")
                candidate = json.loads(evaluated_bytes)
        except (json.JSONDecodeError, OSError, UnicodeError):
            candidate_parse_ok = False

        if not isinstance(candidate, dict):
            candidate_parse_ok = False
            candidate = {}

        primitive = target.get("primitive")
        if primitive == "ECDSA_Nonce_Reuse":
            crypto_ok, crypto_details = self._frozen.ecdsa_valid(target, candidate)
        elif primitive == "ChaCha20_Nonce_Repeat":
            crypto_ok, crypto_details = self._frozen.chacha_valid(target, candidate)
        else:
            crypto_ok, crypto_details = False, {"unsupported_primitive": True}

        if not candidate_parse_ok:
            crypto_ok = False
            crypto_details = dict(crypto_details)
            crypto_details["candidate_unparseable"] = True

        verdict = "ACCEPTED" if crypto_ok else "REJECTED"

        facts = {
            "verifier_version": VERIFIER_VERSION,
            "primitive": primitive,
            "verdict": verdict,
            "cryptographic_predicate": bool(crypto_ok),
            "crypto_details": crypto_details,
            "target_state_sha256": target_sha,
            "stdout_sha256": stdout_sha,
            "candidate_sha256": sha256_bytes(evaluated_bytes),
            "candidate_bytes": len(evaluated_bytes),
            "candidate_parse_ok": candidate_parse_ok,
            "attempt_id": attempt_id,
            "session_id": session_id,
            "epoch": int(epoch),
            "target_id": target_id,
            "parser": "json-last-line-v1",
            "predicate_source": "frozen:contract_sound_stage01_reference_verifier_v2.py",
        }

        context = build_context(KIND_REFERENCE_VERDICT, ROLE_REFERENCE_VERIFIER,
                                target_id, attempt_id, epoch)
        payload = {
            "context": context,
            "context_signature_hex": sign_context_bytes(self._private_key, context),
            "facts": facts,
        }

        from protected_signing import SignRequest, sign_record

        record = sign_record(
            self.key_path,
            SignRequest(kind=KIND_REFERENCE_VERDICT, context=SIGNING_CONTEXT, payload=payload),
            issuer_policy(),
        )
        return {"record": record, "context": context, "facts": facts, "verdict": verdict}
