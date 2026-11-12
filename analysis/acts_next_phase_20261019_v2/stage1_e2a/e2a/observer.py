"""TRUSTED Execution Observer (TEO).

The TEO is the only component in the E2A contract that is allowed to assert
anything about *program execution*.  It:

1. screens the untrusted program source against a declared interface;
2. writes the program bytes into an anonymous in-memory file (``memfd``),
   computes SHA-256 over **exactly those bytes**, and executes the
   interpreter against ``/proc/self/fd/<n>`` with the descriptor inherited.
   The bytes that are hashed are therefore provably the bytes that are
   executed; the write-then-hash-then-execute TOCTOU window of the production
   Stage 01 runner (``run_contract_sound_agent_pilot.py`` lines 59-63) does
   not exist here;
3. captures stdout/stderr and the return code itself;
4. parses the candidate output **from its own capture** and pins the digest
   of the exact stdout byte string it observed;
5. emits a signed observation record whose payload carries the whole causal
   chain prefix (producer identity, program bytes, invocation, environment,
   input, target, attempt, captured output, parsed output).

The TEO never receives a digest, a claim, or a verdict from the producer.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):  # pragma: no cover - direct execution support
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from e2a import canonical, remediation
else:
    from . import canonical, remediation

# --- declared program interface (the E2A boundary) ---------------------------

# Imports the producer program may use.  ``open`` is *not* banned: the
# historical Stage 01 screen banned the token ``open(`` and therefore
# rejected every program that actually read the instance file it was told to
# read (E2A_PREREGISTRATION, Finding F-2).  Here reading is permitted, while
# process creation, networking, dynamic import and filesystem mutation are
# not.
ALLOWED_IMPORTS = frozenset({"json", "sys", "base64", "binascii", "hashlib"})

# Banned substrings inside call/attribute expressions.
BANNED_TOKENS = (
    "subprocess", "socket", "requests", "urllib", "ftplib", "ctypes",
    "os.system", "os.popen", "os.remove", "os.unlink", "os.rmdir",
    "os.exec", "os.spawn", "shutil", "importlib", "multiprocessing",
    "pickle", "marshal", "tempfile", "pathlib", "platform", "getpass",
    "webbrowser", "signal", "fcntl", "mmap", "pty", "eval(", "exec(",
    "compile(", "__import__",
)

EXEC_TIMEOUT_SECONDS = 120
SCREEN_LABEL = "e2a-screen-v1"


def screen_source(source: str) -> tuple[bool, str]:
    """Screen untrusted program source against the declared interface.

    Returns ``(accepted, reason)``.  The screen restricts the *interface*; it
    is not a sandbox (E2A_PREREGISTRATION, threat 4).
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return False, f"syntax:{exc.msg}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                    return False, "disallowed-import"
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in ALLOWED_IMPORTS:
                return False, "disallowed-import"
        elif isinstance(node, (ast.Call, ast.Attribute)):
            text = ast.unparse(node)
            for token in BANNED_TOKENS:
                if token in text:
                    return False, "disallowed-boundary"
    return True, "syntax-and-boundary-pass"


def parse_candidate_output(stdout_bytes: bytes) -> dict[str, Any]:
    """Parse the captured stdout into a candidate output.

    The E2A contract requires **exactly one** non-empty stdout line that
    parses as a JSON *object*.  The historical Stage 01 runner instead took
    the *last* non-empty line, which is an output-substitution surface: a
    program may print an honest claim and then a second, different claim, and
    the historical parser would keep the second.  The strict rule is recorded
    here together with the historical last-line result so that the two rules
    can be compared (secondary metric, ablation).
    """
    text = stdout_bytes.decode("utf-8", errors="replace")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    result: dict[str, Any] = {
        "stdout_line_count": len(lines),
        "stdout_lines_sha256": canonical.sha_bytes("\n".join(lines).encode("utf-8")),
        "parse_status": "EMPTY",
        "parsed_candidate": None,
        "parsed_candidate_sha256": None,
        "parsed_candidate_lastline": None,
        "parsed_candidate_lastline_sha256": None,
    }
    if not lines:
        return result
    try:
        last = json.loads(lines[-1])
    except json.JSONDecodeError:
        result["parse_status"] = "NON_JSON" if len(lines) == 1 else "AMBIGUOUS_MULTIPLE_LINES"
        return result
    if isinstance(last, dict):
        result["parsed_candidate_lastline"] = last
        result["parsed_candidate_lastline_sha256"] = canonical.sha_object(last)
    if len(lines) != 1:
        result["parse_status"] = "AMBIGUOUS_MULTIPLE_LINES"
        return result
    try:
        parsed = json.loads(lines[0])
    except json.JSONDecodeError:
        result["parse_status"] = "NON_JSON"
        return result
    if not isinstance(parsed, dict):
        result["parse_status"] = "NOT_AN_OBJECT"
        return result
    result["parse_status"] = "OK"
    result["parsed_candidate"] = parsed
    result["parsed_candidate_sha256"] = canonical.sha_object(parsed)
    return result


def _interpreter_identity() -> dict[str, Any]:
    executable = Path(sys.executable).resolve()
    try:
        digest = canonical.sha_file(executable)
    except OSError:
        digest = None
    return {
        "interpreter_path": str(executable),
        "interpreter_sha256": digest,
        "interpreter_version": platform.python_version(),
        "interpreter_implementation": platform.python_implementation(),
    }


def _execution_environment() -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONHASHSEED": "0",
        "PYTHONIOENCODING": "utf-8",
    }


def execute_observed(source_bytes: bytes, instance_path: Path, case_dir: Path) -> dict[str, Any]:
    """Execute *source_bytes* from an anonymous in-memory file and capture output.

    The program is executed from ``/proc/self/fd/<n>``; the descriptor is
    inherited by the child, so the interpreter reads exactly the bytes that
    were hashed.
    """
    environment = _execution_environment()
    descriptor = os.memfd_create("e2a-candidate.py", 0)
    try:
        os.write(descriptor, source_bytes)
        os.lseek(descriptor, 0, os.SEEK_SET)
        # cwd is case_dir, so pass the bare instance filename (not the absolute
        # path) to avoid a double join: cwd/instance_path would resolve to
        # case_dir/case_dir/public_instance.json.
        command = [sys.executable, "-I", f"/proc/self/fd/{descriptor}", instance_path.name]
        timed_out = False
        try:
            completed = subprocess.run(
                command,
                cwd=str(case_dir),
                env=environment,
                capture_output=True,
                timeout=EXEC_TIMEOUT_SECONDS,
                pass_fds=(descriptor,),
                check=False,
            )
            stdout_bytes = completed.stdout
            stderr_bytes = completed.stderr
            returncode = completed.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout_bytes = exc.stdout or b""
            stderr_bytes = exc.stderr or b""
            returncode = None
    finally:
        os.close(descriptor)
    return {
        "command": command,
        "environment": environment,
        "stdout_bytes": stdout_bytes,
        "stderr_bytes": stderr_bytes,
        "returncode": returncode,
        "timed_out": timed_out,
    }


def observe(spec: dict[str, Any], keys_dir: Path, bundle_path: Path, policy_path: Path) -> dict[str, Any]:
    """Run the full TEO observation for one case and return the signed envelope."""
    signing = remediation.protected_signing()
    context_module = remediation.context_validator()
    policy, _policy_document = remediation.load_policy(policy_path)

    case_dir = Path(spec["case_dir"])
    case_dir.mkdir(parents=True, exist_ok=True)
    source_text = spec["program_source_text"]
    source_bytes = source_text.encode("utf-8")

    accepted, screen_reason = screen_source(source_text)

    instance = spec["public_instance"]
    instance_bytes = canonical.canonical_bytes(instance)
    instance_path = case_dir / "public_instance.json"
    instance_path.write_bytes(instance_bytes)

    # Retain the exact source bytes as an artifact (the file the certificate
    # may name).  The digest below is over the bytes that are executed.
    source_artifact = case_dir / "program_source.py"
    source_artifact.write_bytes(source_bytes)

    observation: dict[str, Any] = {
        "case_id": spec["case_id"],
        "producer": spec["producer"],
        "screen": {"label": SCREEN_LABEL, "accepted": accepted, "reason": screen_reason},
        "program_source_sha256": canonical.sha_bytes(source_bytes),
        "program_source_length": len(source_bytes),
        "program_source_artifact_path": str(source_artifact),
        "public_instance_sha256": canonical.sha_bytes(instance_bytes),
        "public_target_digest": canonical.sha_object(instance),
        "target_id": spec["target_id"],
        "attempt_id": spec["attempt_id"],
        "epoch": spec["epoch"],
        "interpreter": _interpreter_identity(),
        "environment": _execution_environment(),
    }

    if not accepted:
        observation.update({
            "execution_status": "SCREEN_REJECTED",
            "command": None,
            "stdout_sha256": None,
            "stderr_sha256": None,
            "stdout_length": 0,
            "stderr_length": 0,
            "returncode": None,
            "timed_out": False,
            "parse": parse_candidate_output(b""),
        })
    else:
        result = execute_observed(source_bytes, instance_path, case_dir)
        (case_dir / "executor_stdout.txt").write_bytes(result["stdout_bytes"])
        (case_dir / "executor_stderr.txt").write_bytes(result["stderr_bytes"])
        observation.update({
            "execution_status": "EXECUTED" if result["returncode"] == 0 else "EXECUTION_FAILED",
            "command": result["command"],
            "environment": result["environment"],
            "stdout_sha256": canonical.sha_bytes(result["stdout_bytes"]),
            "stderr_sha256": canonical.sha_bytes(result["stderr_bytes"]),
            "stdout_length": len(result["stdout_bytes"]),
            "stderr_length": len(result["stderr_bytes"]),
            "stdout_path": str(case_dir / "executor_stdout.txt"),
            "stderr_path": str(case_dir / "executor_stderr.txt"),
            "returncode": result["returncode"],
            "timed_out": result["timed_out"],
            "parse": parse_candidate_output(result["stdout_bytes"]),
        })
        if observation["parse"]["parse_status"] == "OK":
            canonical.write_canonical_json(case_dir / "candidate_output.json", observation["parse"]["parsed_candidate"])

    # Sign the six-field context with the issuer's Ed25519 key, using the
    # audited canonicalisation from context_validator.
    context = dict(spec["context"])
    key_path = _key_path_for_role(keys_dir, remediation.ROLE_OBSERVER)
    _key_id, role, private_key = signing.load_private_key(key_path)
    context_signature = private_key.sign(context_module.canonical_context(context)).hex()

    record = signing.sign_record(
        key_path,
        signing.SignRequest(kind=canonical.OBSERVATION_KIND, context=canonical.POLICY_CONTEXT,
                            payload={**observation, "context": context}),
        policy,
    )
    envelope = {
        "schema": "e2a-signed-record/1",
        "kind": canonical.OBSERVATION_KIND,
        "issuer_role": role,
        "record": record,
        "context": context,
        "context_signature_hex": context_signature,
    }
    return envelope


def _key_path_for_role(keys_dir: Path, role: str) -> Path:
    for candidate in sorted(Path(keys_dir).glob("*.json")):
        record = json.loads(candidate.read_text(encoding="utf-8"))
        if record.get("role") == role:
            return candidate
    raise KeyError(f"no private key for role {role!r} in {keys_dir}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="E2A trusted execution observer")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--keys", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    args = parser.parse_args(argv)

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    envelope = observe(spec, args.keys, args.bundle, args.policy)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(canonical.canonical_bytes(envelope))
    print(json.dumps({"case_id": envelope["record"]["payload"]["case_id"],
                      "execution_status": envelope["record"]["payload"]["execution_status"],
                      "parse_status": envelope["record"]["payload"]["parse"]["parse_status"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
