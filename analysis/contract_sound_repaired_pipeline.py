#!/usr/bin/env python3
"""Offline-only repaired contract-sound pipeline.

This module never calls a provider. It repairs two deterministic defects:
1. subprocess reference inputs are passed as path strings, not Path objects;
2. the declared argv[1] JSON interface permits only read-only open(sys.argv[1]).
All other filesystem/network/process boundaries remain rejected.
"""
from __future__ import annotations
import ast, json, os, resource, shutil, subprocess, sys
from pathlib import Path

ALLOWED_IMPORTS = {"json", "sys", "base64"}
FORBIDDEN_BOUNDARIES = {"subprocess", "socket", "requests", "urllib", "os.", "__import__"}


def _is_allowed_instance_read(node: ast.Call) -> bool:
    if not isinstance(node.func, ast.Name) or node.func.id != "open":
        return False
    if len(node.args) not in (1, 2) or node.keywords:
        return False
    arg = node.args[0]
    if not (isinstance(arg, ast.Subscript)
            and isinstance(arg.value, ast.Attribute)
            and isinstance(arg.value.value, ast.Name)
            and arg.value.value.id == "sys"
            and arg.value.attr == "argv"
            and isinstance(arg.slice, ast.Constant)
            and arg.slice.value == 1):
        return False
    if len(node.args) == 2:
        mode = node.args[1]
        if not isinstance(mode, ast.Constant) or mode.value not in {"r", "rt"}:
            return False
    return True


def qualify_source(source: str) -> tuple[bool, str, list[dict]]:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return False, "SOURCE_PARSE_REJECTED", [{"rule": "syntax", "message": exc.msg, "line": exc.lineno}]
    violations: list[dict] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in ALLOWED_IMPORTS:
                    violations.append({"rule": "disallowed-import", "value": alias.name, "line": node.lineno})
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in ALLOWED_IMPORTS:
                violations.append({"rule": "disallowed-import-from", "value": node.module, "line": node.lineno})
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                if not _is_allowed_instance_read(node):
                    violations.append({"rule": "disallowed-boundary", "value": "open:not-readonly-argv1", "line": node.lineno})
                continue
            text = ast.unparse(node)
            hits = sorted({token for token in FORBIDDEN_BOUNDARIES if token in text})
            if hits:
                violations.append({"rule": "disallowed-boundary", "value": hits, "line": getattr(node, "lineno", None), "expression": text[:240]})
        elif isinstance(node, ast.Attribute):
            text = ast.unparse(node)
            hits = sorted({token for token in FORBIDDEN_BOUNDARIES if token in text})
            if hits:
                violations.append({"rule": "disallowed-boundary", "value": hits, "line": getattr(node, "lineno", None), "expression": text[:240]})
    return (not violations, "QUALIFIED" if not violations else "SANDBOX_REJECTED", violations)


def _limit_child_resources() -> None:
    """Apply bounded, fail-closed limits inside the candidate process."""
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))


def _sandbox_command(candidate_path: Path, input_path: Path, case_dir: Path) -> list[str]:
    """Return an OS-isolated command; refuse execution if isolation is unavailable."""
    bwrap = shutil.which("bwrap")
    if not bwrap:
        raise RuntimeError("OS_SANDBOX_UNAVAILABLE:bwrap-not-found")
    # The host filesystem is visible read-only; only the per-case directory is
    # writable.  The network namespace is empty, so AST policy is not the sole
    # network boundary.  The input is still passed only through argv[1].
    return [
        bwrap,
        "--die-with-parent",
        "--unshare-net",
        "--ro-bind", "/", "/",
        "--bind", str(case_dir), str(case_dir),
        "--chdir", str(case_dir),
        "--",
        sys.executable,
        "-I",
        str(candidate_path),
        str(input_path),
    ]


def execute_candidate(source: str, instance: dict, case_dir: Path, timeout: int = 30) -> dict:
    case_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = case_dir / "candidate.py"
    input_path = case_dir / "public_instance.json"
    stdout_path = case_dir / "executor_stdout.txt"
    stderr_path = case_dir / "executor_stderr.txt"
    output_path = case_dir / "candidate_output.json"
    candidate_path.write_text(source)
    input_path.write_text(json.dumps(instance, sort_keys=True) + "\n")
    qualified, stage, violations = qualify_source(source)
    if not qualified:
        return {"status": stage, "qualification": violations, "artifact_path": str(candidate_path), "stderr_path": str(stderr_path)}
    env = {"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0"}
    try:
        command = _sandbox_command(candidate_path, input_path, case_dir)
        proc = subprocess.run(
            command,
            cwd=case_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            start_new_session=True,
            preexec_fn=_limit_child_resources,
        )
    except RuntimeError as exc:
        return {"status": "SANDBOX_UNAVAILABLE", "reason": str(exc), "artifact_path": str(candidate_path), "stderr_path": str(stderr_path)}
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        stdout_path.write_text(stdout)
        stderr_path.write_text(stderr)
        return {"status": "EXECUTION_TIMEOUT", "artifact_path": str(candidate_path), "stdout_path": str(stdout_path), "stderr_path": str(stderr_path)}
    stdout_path.write_text(proc.stdout)
    stderr_path.write_text(proc.stderr)
    if proc.returncode != 0:
        return {"status": "EXECUTION_FAILED", "returncode": proc.returncode, "artifact_path": str(candidate_path), "stdout_path": str(stdout_path), "stderr_path": str(stderr_path)}
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    try:
        output = json.loads(lines[-1]) if lines else None
    except json.JSONDecodeError as exc:
        return {"status": "CANDIDATE_OUTPUT_INVALID", "reason": "malformed-json", "error": str(exc), "artifact_path": str(candidate_path), "stdout_path": str(stdout_path), "stderr_path": str(stderr_path)}
    if not isinstance(output, dict):
        return {"status": "CANDIDATE_OUTPUT_INVALID", "reason": "not-json-object", "artifact_path": str(candidate_path), "stdout_path": str(stdout_path), "stderr_path": str(stderr_path)}
    output_path.write_text(json.dumps(output, sort_keys=True) + "\n")
    return {"status": "EXECUTED", "output": output, "artifact_path": str(candidate_path), "output_path": str(output_path), "stdout_path": str(stdout_path), "stderr_path": str(stderr_path), "returncode": 0}


def invoke_reference(script: Path, bundle_path: Path) -> dict:
    proc = subprocess.run([sys.executable, str(script), str(bundle_path)], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return {"reference_process": "FAILED", "returncode": proc.returncode, "stderr": proc.stderr, "stdout": proc.stdout}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {"reference_process": "INVALID_OUTPUT", "error": str(exc), "stderr": proc.stderr, "stdout": proc.stdout}


def invoke_validator(script: Path, public_cert: dict) -> dict:
    payload = json.dumps(public_cert, sort_keys=True).encode()
    proc = subprocess.run([sys.executable, str(script)], input=payload, capture_output=True, check=False)
    if proc.returncode != 0:
        return {"validator_process": "FAILED", "returncode": proc.returncode, "stderr": proc.stderr.decode(errors="replace")}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {"validator_process": "INVALID_OUTPUT", "error": str(exc), "stderr": proc.stderr.decode(errors="replace")}
