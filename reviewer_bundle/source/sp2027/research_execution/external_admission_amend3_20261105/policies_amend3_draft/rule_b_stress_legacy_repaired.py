#!/usr/bin/env python3
# POLICY SNAPSHOT — Rule (b2) AMENDMENT 3, proposed 2026-11-05 (DRAFT, NOT YET FROZEN).
# Base: rule_a_permissive_v4.py (2026-10-29) — VERBATIM copy, header replaced only.
# Semantics: OUR counterfactual stress rule (legacy import set {json, sys, base64},
# provenance h1r3_contract POLICIES["legacy"]) WITH the same registered read-boundary
# repair that Amendment 2 applied to the declared arm. The repair is an interface
# fix, not a policy axis, so it is applied to BOTH arms up front in Amendment 3
# (this closes the disclosed post-outcome deviation of amendment 2: 'boundary fix
# applied to both arms' is now the registered design, not an analysis repair).
# Compile with: imports+boundary+the other frozen checks; POLICIES['legacy'] is
# the stress import set; qualify_source(source, policy='legacy') is the arm call.
# Do not edit after freeze; changes require a new preregistration amendment.

import ast

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
    """True when the call is a read-only access to the sandboxed instance.

    Amendment 2 adds the literal-filename branch: the sandbox hands the instance
    to external programs as `output.txt` in the working directory, so
    open("output.txt", "r") is the same read authority as open(sys.argv[1], "r").
    Bare names only (no separators, no "."/".."), read-only modes only.
    """
    if not isinstance(node.func, ast.Name) or node.func.id != "open":
        return False
    if len(node.args) not in (1, 2) or node.keywords:
        return False
    arg = node.args[0]

    # --- amendment 2 branch -------------------------------------------------
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        name = arg.value
        if not name or "/" in name or "\\" in name or name in (".", ".."):
            return False
        if len(node.args) == 1:
            return True
        mode = node.args[1]
        return isinstance(mode, ast.Constant) and mode.value in {"r", "rt", "rb"}
    # --- end amendment 2 branch ---------------------------------------------

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


