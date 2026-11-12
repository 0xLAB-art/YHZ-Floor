#!/usr/bin/env python3
"""H1-R3 execution contract: symmetric qualification policy and OS sandbox.

Two policies are implemented so that the historical import policy can be
re-evaluated offline against the same generated programs without any rerun:

  legacy  : the frozen 2026-10-18 pilot policy (json, sys, base64 only)
  v3      : the prospective symmetric policy used for all arms in H1-R3

v3 admits computationally inert standard-library modules (hashlib, math, ...)
and continues to reject every process, network, and filesystem capability.
The change is symmetric across arms and is fixed before any model call.

Candidate code is executed inside bubblewrap with an empty network namespace,
a read-only host mount, a single writable per-case directory, `python -I`,
and CPU/address-space/file-size/file-descriptor limits.
"""
from __future__ import annotations

import ast
import json
import os
import resource
import shutil
import subprocess
import sys
from pathlib import Path

POLICIES = {
    "legacy": {"json", "sys", "base64"},
    "v3": {
        "base64", "binascii", "collections", "decimal", "fractions", "functools",
        "hashlib", "itertools", "json", "math", "operator", "re", "statistics",
        "string", "struct", "sys", "typing",
    },
}

FORBIDDEN_MODULES = {
    "os", "pathlib", "shutil", "socket", "urllib", "http", "requests", "subprocess",
    "importlib", "ctypes", "multiprocessing", "threading", "asyncio", "signal",
    "pickle", "marshal", "tempfile", "glob", "io", "builtins",
}
FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__", "input", "globals", "locals", "vars"}
FORBIDDEN_SUBSTRINGS = ("__globals__", "__subclasses__", "__builtins__", "__class__", "__mro__", "__code__")


def _is_allowed_instance_read(node: ast.Call) -> bool:
    if not isinstance(node.func, ast.Name) or node.func.id != "open":
        return False
    if len(node.args) not in (1, 2) or node.keywords:
        return False
    arg = node.args[0]
    if not (
        isinstance(arg, ast.Subscript)
        and isinstance(arg.value, ast.Attribute)
        and isinstance(arg.value.value, ast.Name)
        and arg.value.value.id == "sys"
        and arg.value.attr == "argv"
        and isinstance(arg.slice, ast.Constant)
        and arg.slice.value == 1
    ):
        return False
    if len(node.args) == 2:
        mode = node.args[1]
        if not isinstance(mode, ast.Constant) or mode.value not in {"r", "rt"}:
            return False
    return True


def qualify_source(source: str, policy: str = "v3") -> dict:
    """Return a structured qualification decision under one policy."""
    allowed = POLICIES[policy]
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {"qualified": False, "status": "SOURCE_PARSE_REJECTED", "policy": policy,
                "violations": [{"rule": "syntax", "message": exc.msg, "line": exc.lineno}]}

    violations: list[dict] = []
    imported: set[str] = set()
    referenced: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            referenced.add(node.id)
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                imported.add(root)
                if root not in allowed:
                    violations.append({"rule": "disallowed-import", "value": alias.name, "line": node.lineno})
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            imported.add(root)
            for alias in node.names:
                imported.add(alias.name)
            if root not in allowed:
                violations.append({"rule": "disallowed-import-from", "value": node.module, "line": node.lineno})
        elif isinstance(node, ast.Attribute):
            text = ast.unparse(node)
            if any(token in text for token in FORBIDDEN_SUBSTRINGS):
                violations.append({"rule": "disallowed-dunder", "value": text[:120], "line": node.lineno})
            root = text.split(".")[0]
            if root in FORBIDDEN_MODULES:
                violations.append({"rule": "disallowed-module-access", "value": root, "line": node.lineno})
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                if not _is_allowed_instance_read(node):
                    violations.append({"rule": "disallowed-boundary", "value": "open:not-readonly-argv1", "line": node.lineno})
                continue
            if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
                violations.append({"rule": "disallowed-call", "value": node.func.id, "line": node.lineno})
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_MODULES and policy == "v3":
            violations.append({"rule": "disallowed-name", "value": node.id, "line": getattr(node, "lineno", None)})

    unused_imports = sorted({name for name in imported if name not in referenced})
    return {
        "qualified": not violations,
        "status": "QUALIFIED" if not violations else "SANDBOX_REJECTED",
        "policy": policy,
        "violations": violations,
        "imported_modules": sorted(imported),
        "unused_imports": unused_imports,
    }


def _limit_child_resources() -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))


def sandbox_command(candidate_path: Path, input_path: Path, case_dir: Path) -> list[str]:
    for path in (candidate_path, input_path, case_dir):
        if not Path(path).is_absolute():
            raise RuntimeError(f"OS_SANDBOX_PATH_NOT_ABSOLUTE:{path}")
    bwrap = shutil.which("bwrap")
    if not bwrap:
        raise RuntimeError("OS_SANDBOX_UNAVAILABLE:bwrap-not-found")
    return [
        bwrap,
        "--die-with-parent",
        "--unshare-net",
        "--unshare-pid",
        "--ro-bind", "/", "/",
        # The per-case directory is the only writable path; it is bound after
        # the read-only root so it takes precedence at that exact path.
        "--bind", str(case_dir), str(case_dir),
        "--chdir", str(case_dir),
        "--",
        sys.executable,
        "-I",
        str(candidate_path),
        str(input_path),
    ]


def execute_candidate(source: str, instance_text: str, case_dir: Path, timeout: int = 20,
                      policy: str = "v3") -> dict:
    # bwrap performs --chdir inside the new mount namespace, so every path must
    # be absolute before it reaches the sandbox command.
    case_dir = Path(case_dir).resolve()
    case_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = case_dir / "candidate.py"
    input_path = case_dir / "public_instance.json"
    stdout_path = case_dir / "executor_stdout.txt"
    stderr_path = case_dir / "executor_stderr.txt"
    output_path = case_dir / "candidate_output.json"
    candidate_path.write_text(source)
    input_path.write_text(instance_text if instance_text.endswith("\n") else instance_text + "\n")

    decision = qualify_source(source, policy)
    if not decision["qualified"]:
        return {"status": decision["status"], "qualification": decision,
                "artifact_path": str(candidate_path), "stderr_path": str(stderr_path)}

    env = {"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        command = sandbox_command(candidate_path, input_path, case_dir)
        proc = subprocess.run(
            command, cwd=case_dir, env=env, capture_output=True, text=True,
            timeout=timeout, check=False, start_new_session=True,
            preexec_fn=_limit_child_resources,
        )
    except RuntimeError as exc:
        return {"status": "SANDBOX_UNAVAILABLE", "reason": str(exc),
                "artifact_path": str(candidate_path), "stderr_path": str(stderr_path)}
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        stdout_path.write_text(stdout)
        stderr_path.write_text(stderr)
        return {"status": "EXECUTION_TIMEOUT", "artifact_path": str(candidate_path),
                "stdout_path": str(stdout_path), "stderr_path": str(stderr_path)}

    stdout_path.write_text(proc.stdout)
    stderr_path.write_text(proc.stderr)
    if proc.returncode != 0:
        return {"status": "EXECUTION_FAILED", "returncode": proc.returncode,
                "artifact_path": str(candidate_path), "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path)}
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        return {"status": "OUTPUT_SCHEMA_INVALID", "reason": "empty-stdout",
                "artifact_path": str(candidate_path), "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path)}
    try:
        output = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        return {"status": "OUTPUT_SCHEMA_INVALID", "reason": "malformed-json", "error": str(exc),
                "artifact_path": str(candidate_path), "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path)}
    if not isinstance(output, dict):
        return {"status": "OUTPUT_SCHEMA_INVALID", "reason": "not-json-object",
                "artifact_path": str(candidate_path), "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path)}
    output_path.write_text(json.dumps(output, sort_keys=True) + "\n")
    return {"status": "EXECUTED", "output": output, "artifact_path": str(candidate_path),
            "output_path": str(output_path), "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path), "returncode": 0,
            "qualification": decision, "extra_stdout_lines": max(0, len(proc.stdout.splitlines()) - 1)}


def check_output_schema(family: str, require_k: bool, output: dict, target_length: int | None) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if family == "XOR_Keystream_Reuse":
        value = output.get("plaintext")
        if not isinstance(value, str):
            errors.append("missing-or-nonstring-plaintext")
        elif target_length is not None and len(value) != 2 * target_length:
            errors.append(f"length:{len(value)}!={2 * target_length}")
        elif any(c not in "0123456789abcdef" for c in value):
            errors.append("non-lowercase-hex")
    else:
        keys = ["d", "k"] if require_k else ["d"]
        for key in keys:
            value = output.get(key)
            if not isinstance(value, str):
                errors.append(f"missing-or-nonstring-{key}")
            elif len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                errors.append(f"bad-hex-{key}")
    return (not errors), errors


def run_script(script: Path, argv: list[str] | None = None, stdin: str | None = None) -> dict:
    proc = subprocess.run([sys.executable, str(script), *(argv or [])], input=stdin,
                          capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return {"process": "FAILED", "returncode": proc.returncode,
                "stderr": proc.stderr[-4000:], "stdout": proc.stdout[-4000:]}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {"process": "INVALID_OUTPUT", "error": str(exc), "stdout": proc.stdout[-4000:]}
