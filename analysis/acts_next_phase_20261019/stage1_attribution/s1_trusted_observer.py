#!/usr/bin/env python3
"""Trusted execution observer for the Stage 1 attribution experiment (TOEEA-1).

The observer is the component that makes the Stage 1 chain causally grounded.
It is a *different party* from the artifact producer:

  * it holds its own Ed25519 private key, generated fresh at setup time and
    never exposed to the producer (the historical fixtures derived signing
    keys from public session identifiers -- correction C-02 in
    ``scientific_corrections/HISTORICAL_CORRECTION_LEDGER.md``);
  * it reads the program bytes, the invocation, the environment, the captured
    stdout/stderr and the produced output file *itself*, and it signs what it
    read -- so the chain does not rest on hashes supplied by the producer;
  * it writes the parsed output artifact from its own capture of stdout, so the
    output artifact's provenance is the observer's capture rather than the
    producer's assertion.

The observer does not decide whether a claim is justified.  It only records
what happened.  The evaluator in ``s1_attribution_evaluator.py`` decides.
"""
from __future__ import annotations

import ast
import json
import os
import secrets
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from s1_common import (
    CONTEXT_DOMAIN,
    KIND_EXECUTION_OBSERVATION,
    ROLE_EXECUTION_OBSERVER,
    SIGNING_CONTEXT,
    build_context,
    digest_object,
    load_ed25519_private_key,
    read_json,
    sha256_bytes,
    sha256_file,
    sign_context_bytes,
    write_json,
)

OBSERVER_VERSION = "acts-s1-trusted-observer/1"

# Environment variables the observer is willing to expose to the candidate.
ENV_ALLOWLIST = ("PATH", "PYTHONHASHSEED", "LC_ALL")

# Historical restricted-subset policy, reproduced verbatim from
# run_contract_sound_agent_pilot.py:43-54 (allowed imports and forbidden
# boundary tokens).  Reproduced, not imported, so that Stage 1 does not import
# the provider adapter; the equivalence is asserted by a unit test.
POLICY_ALLOWED_IMPORTS = {"json", "sys", "base64"}
POLICY_FORBIDDEN_TOKENS = (
    "subprocess",
    "socket",
    "requests",
    "urllib",
    "os.",
    "open(",
    "__import__",
)


def source_policy(source: str) -> tuple[bool, str]:
    """Apply the historical static source policy; return (ok, reason)."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return False, f"syntax:{exc.msg}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] not in POLICY_ALLOWED_IMPORTS for alias in node.names):
                return False, "disallowed-import"
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] not in POLICY_ALLOWED_IMPORTS:
            return False, "disallowed-import"
        if isinstance(node, (ast.Call, ast.Attribute)):
            text = ast.unparse(node)
            if any(token in text for token in POLICY_FORBIDDEN_TOKENS):
                return False, "disallowed-boundary"
    return True, "syntax-and-boundary-pass"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class TrustedObserver:
    """Executes a candidate program and signs an observation of that execution."""

    def __init__(self, key_path: Path, workdir: Path, *, enforce_source_policy: bool = True,
                 timeout_seconds: int = 120) -> None:
        self.key_path = Path(key_path)
        self.workdir = Path(workdir)
        self.enforce_source_policy = enforce_source_policy
        self.timeout_seconds = timeout_seconds
        self._private_key = load_ed25519_private_key(self.key_path)

    # -- internals ---------------------------------------------------------
    def _sign(self, payload_facts: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        from protected_signing import SignRequest, sign_record

        from s1_common import issuer_policy

        payload = {
            "context": context,
            "context_signature_hex": sign_context_bytes(self._private_key, context),
            "facts": payload_facts,
        }
        record = sign_record(
            self.key_path,
            SignRequest(kind=KIND_EXECUTION_OBSERVATION, context=SIGNING_CONTEXT, payload=payload),
            issuer_policy(),
        )
        return {"record": record, "context": context}

    # -- public API --------------------------------------------------------
    def observe(
        self,
        *,
        program_path: Path,
        input_path: Path,
        attempt_id: str,
        session_id: str,
        epoch: int,
        target_id: str,
        output_name: str = "candidate_output.json",
    ) -> dict[str, Any]:
        """Run the program and return a signed execution observation.

        Returns a dict with the signed ``record``, the parsed ``facts``, the
        on-disk artifacts (stdout, stderr, parsed output) and the raw
        ``status`` of the execution.
        """
        program_path = Path(program_path)
        input_path = Path(input_path)
        case_dir = self.workdir
        case_dir.mkdir(parents=True, exist_ok=True)

        source = program_path.read_text()
        policy_ok, policy_reason = source_policy(source)

        if not policy_ok and self.enforce_source_policy:
            facts = {
                "observer_version": OBSERVER_VERSION,
                "status": "REFUSED_SOURCE_POLICY",
                "source_policy": {"status": "FAIL", "reason": policy_reason},
                "attempt_id": attempt_id,
                "session_id": session_id,
                "epoch": int(epoch),
                "target_id": target_id,
                "program_source_sha256": sha256_file(program_path),
                "executed_program_sha256": None,
                "argv": None,
                "cwd": None,
                "env_allowlist": list(ENV_ALLOWLIST),
                "env_sha256": None,
                "input_sha256": sha256_file(input_path),
                "returncode": None,
                "stdout_sha256": None,
                "stderr_sha256": None,
                "stdout_bytes": 0,
                "stderr_bytes": 0,
                "output_file_present": False,
                "output_file_sha256": None,
                "output_file_bytes": 0,
                "output_parsed": False,
                "observer_nonce": secrets.token_hex(32),
                "started_at": _now_iso(),
                "finished_at": _now_iso(),
                "duration_ms": 0,
                "parser": "json-last-line-v1",
                "boundary": {
                    "enforced": True,
                    "allowed_interface": "argv-instance-json",
                    "restricted_python_subset": sorted(POLICY_ALLOWED_IMPORTS),
                    "network": "none-declared",
                },
            }
            context = build_context(KIND_EXECUTION_OBSERVATION, ROLE_EXECUTION_OBSERVER,
                                    target_id, attempt_id, epoch)
            signed = self._sign(facts, context)
            return {
                "status": "REFUSED_SOURCE_POLICY",
                "record": signed["record"],
                "context": context,
                "facts": facts,
                "stdout_path": None,
                "stderr_path": None,
                "output_path": None,
                "parsed_output": None,
            }

        # Environment actually handed to the child.
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONHASHSEED": "0",
            "LC_ALL": "C",
        }
        argv = [sys.executable, "-I", str(program_path), str(input_path)]

        # Hash the program bytes immediately before exec (TOCTOU window is
        # documented in the protocol; the post-exec hash detects in-place
        # modification by the program itself).
        program_sha_before = sha256_file(program_path)
        input_bytes = input_path.read_bytes()
        input_sha = sha256_bytes(input_bytes)
        stdin_sha = sha256_bytes(input_bytes)

        started_at = _now_iso()
        started = time.monotonic()
        timed_out = False
        try:
            proc = subprocess.run(
                argv,
                cwd=str(case_dir),
                env=env,
                input=input_bytes,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
            stdout_bytes, stderr_bytes, returncode = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout_bytes = exc.stdout or b""
            stderr_bytes = exc.stderr or b""
            returncode = None
        duration_ms = int((time.monotonic() - started) * 1000)
        finished_at = _now_iso()

        program_sha_after = sha256_file(program_path)

        stdout_path = case_dir / "executor_stdout.txt"
        stderr_path = case_dir / "executor_stderr.txt"
        stdout_path.write_bytes(stdout_bytes)
        stderr_path.write_bytes(stderr_bytes)

        # The observer -- not the producer -- derives the output artifact from
        # its own capture of stdout, using the same "json-last-line-v1" parser
        # the historical runner used.
        parsed_output: dict[str, Any] | None = None
        output_parsed = False
        text = stdout_bytes.decode("utf-8", errors="replace")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines:
            try:
                candidate = json.loads(lines[-1])
            except json.JSONDecodeError:
                candidate = None
            if isinstance(candidate, dict):
                parsed_output = candidate
                output_parsed = True

        output_path = case_dir / output_name
        output_present = False
        output_sha = None
        output_len = 0
        if output_parsed:
            write_json(output_path, parsed_output)
            output_present = True
            output_sha = sha256_file(output_path)
            output_len = output_path.stat().st_size

        facts = {
            "observer_version": OBSERVER_VERSION,
            "status": "TIMED_OUT" if timed_out else "EXECUTED",
            "source_policy": {"status": "PASS" if policy_ok else "FAIL", "reason": policy_reason},
            "attempt_id": attempt_id,
            "session_id": session_id,
            "epoch": int(epoch),
            "target_id": target_id,
            "program_source_sha256": program_sha_before,
            "program_source_sha256_after": program_sha_after,
            "executed_program_sha256": program_sha_before,
            "argv": argv,
            "cwd": str(case_dir),
            "env_allowlist": list(ENV_ALLOWLIST),
            "env_sha256": digest_object(env),
            "input_sha256": input_sha,
            "stdin_sha256": stdin_sha,
            "returncode": returncode,
            "stdout_sha256": sha256_bytes(stdout_bytes),
            "stderr_sha256": sha256_bytes(stderr_bytes),
            "stdout_bytes": len(stdout_bytes),
            "stderr_bytes": len(stderr_bytes),
            "output_file_present": output_present,
            "output_file_sha256": output_sha,
            "output_file_bytes": output_len,
            "output_parsed": output_parsed,
            "observer_nonce": secrets.token_hex(32),
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_ms": duration_ms,
            "parser": "json-last-line-v1",
            "boundary": {
                "enforced": True,
                "allowed_interface": "argv-instance-json",
                "restricted_python_subset": sorted(POLICY_ALLOWED_IMPORTS),
                "network": "none-declared",
            },
        }
        context = build_context(KIND_EXECUTION_OBSERVATION, ROLE_EXECUTION_OBSERVER,
                                target_id, attempt_id, epoch)
        signed = self._sign(facts, context)
        return {
            "status": facts["status"],
            "record": signed["record"],
            "context": context,
            "facts": facts,
            "stdout_path": stdout_path,
            "stderr_path": stderr_path,
            "output_path": output_path if output_present else None,
            "parsed_output": parsed_output,
        }
