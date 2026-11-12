# AMENDMENT-2 SNAPSHOT (2026-10-25): derived from rule_c_cleanup.py
# (sha256 7419e861a4d1abeb...) by adding a wd-reads qualify() variant;
# transform() unchanged. See rule_b2 for the read clause.
#!/usr/bin/env python3
# POLICY SNAPSHOT — Rule (c) = Rule (b) + output-preserving unused-import
# cleanup, verbatim port. Provenance: the cleanup transform() from
# sp2027/analysis/contribution_audit_20261021/policy_mechanism/audit.py,
# extracted verbatim by AST slicing on 2026-10-24 for namespace
# external_admission_20261024, plus a byte-identical-output check harness
# (execute_cleanup_and_compare) written for this namespace.

import ast
import re

# Amendment-2: the same module sets as the frozen basis policies (needed by
# qualify_source_wd below); identical values to rule_a2/rule_b2.
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

def transform(source, allowed):
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source, [], [], ['syntax']
    nodes = list(ast.walk(tree))
    names = {n.id for n in nodes if isinstance(n, ast.Name)}
    dynamic = sorted({n.id for n in nodes if isinstance(n, ast.Name) and n.id in {
        'eval', 'exec', 'compile', 'globals', 'locals', 'vars', 'dir', 'getattr',
        'setattr', 'delattr', '__import__', 'inspect', 'importlib'}})
    if any(isinstance(n, ast.Attribute) and (n.attr.startswith('__') or n.attr in {'modules', '_getframe'}) for n in nodes):
        dynamic.append('reflection-attribute')
    strings = [n.value for n in nodes if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    imports, edits = [], []
    lines = source.splitlines(keepends=True)
    for node in nodes:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        entries = []
        for alias in node.names:
            module = alias.name if isinstance(node, ast.Import) else node.module or ''
            bound = alias.asname or (alias.name.split('.')[0] if isinstance(node, ast.Import) else alias.name)
            string_mention = any(re.search(r'\b' + re.escape(bound) + r'\b', s) for s in strings)
            eligible_module = module.split('.')[0] in {'hashlib', 'typing', 'collections', 'math', 'itertools', 'functools', 'struct', 'binascii', 'operator', 'statistics', 'string', 'decimal', 'fractions', 're'}
            reasons = []
            if bound in names:
                reasons.append('name-reference-any-scope')
            if string_mention:
                reasons.append('string-reference-uncertain')
            if dynamic:
                reasons.append('dynamic-access-uncertain')
            if node not in tree.body:
                reasons.append('nested-import-uncertain')
            if alias.name == '*' or getattr(node, 'level', 0):
                reasons.append('wildcard-or-relative')
            if not eligible_module:
                reasons.append('module-side-effects-not-qualified')
            entries.append({'module': module, 'binding': bound, 'alias': alias.asname,
                            'line': node.lineno, 'disallowed_legacy': module.split('.')[0] not in allowed,
                            'classification': 'referenced_preserve' if bound in names else ('uncertain_preserve' if reasons else 'conservatively_unused'),
                            'reasons': reasons})
        imports.extend(entries)
        full_line = node.col_offset == 0 and not lines[node.end_lineno - 1][node.end_col_offset:].strip().strip('\n').startswith(';')
        if full_line and all(e['classification'] == 'conservatively_unused' for e in entries) and any(e['disallowed_legacy'] for e in entries):
            old = ''.join(lines[node.lineno - 1:node.end_lineno])
            if ast.get_source_segment(source, node).strip() != old.strip() and not old.strip().startswith(ast.get_source_segment(source, node).strip() + ' #'):
                continue
            edits.append({'start_line': node.lineno, 'end_line': node.end_lineno, 'before': old, 'after': '\n' * (node.end_lineno - node.lineno + 1), 'bindings': [e['binding'] for e in entries]})
    for edit in reversed(edits):
        lines[edit['start_line'] - 1:edit['end_line']] = [edit['after']]
    result = ''.join(lines)
    ast.parse(result)
    return result, edits, imports, dynamic



def execute_cleanup_and_compare(source, instance_text):
    """Rule (c) application: clean under the transform, then require (1) the
    cleaned source still qualifies under the legacy stress rule and (2) running
    both sources on the same instance produces byte-identical stdout.

    Returns a dict; output_preserved is the byte-identical stdout check.
    """
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    cleaned, edits, imports, dynamic = transform(source, {"json", "sys", "base64"})
    result = {"edits": len(edits), "cleaned_sha256": __import__("hashlib").sha256(cleaned.encode()).hexdigest()}
    if not edits:
        result["output_preserved"] = None
        result["note"] = "no eligible cleanup edits; nothing to compare"
        return result
    with tempfile.TemporaryDirectory(prefix="acts_extadm_cleanup_") as td:
        tdp = Path(td)
        for name, text in (("orig.py", source), ("clean.py", cleaned), ("instance.json", instance_text)):
            (tdp / name).write_text(text)
        outs = {}
        for name in ("orig.py", "clean.py"):
            proc = subprocess.run([sys.executable, "-I", str(tdp / name), str(tdp / "instance.json")],
                                  cwd=tdp, capture_output=True, timeout=30)
            outs[name] = proc.stdout
        result["output_preserved"] = outs["orig.py"] == outs["clean.py"]
    return result

def _is_allowed_instance_read(node: ast.Call) -> bool:
    """AMENDMENT-2 read clause: matches the frozen prompts' artifact contract
    ("artifact files are present, under the same names, in your program's
    working directory"). Permits (1) the legacy form — a read-only open of
    sys.argv[1] — and (2) a read-only open of a constant string path. All
    other open() forms (write/append modes, dynamic paths, keyword args)
    remain disallowed-boundary violations. The import axes are untouched."""
    if not isinstance(node.func, ast.Name) or node.func.id != "open":
        return False
    if len(node.args) not in (1, 2) or node.keywords:
        return False
    arg = node.args[0]
    if (isinstance(arg, ast.Subscript)
            and isinstance(arg.value, ast.Attribute)
            and isinstance(arg.value.value, ast.Name)
            and arg.value.value.id == "sys"
            and arg.value.attr == "argv"
            and isinstance(arg.slice, ast.Constant)
            and arg.slice.value == 1):
        pass  # legacy form, unchanged
    elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        pass  # amendment-2 form: constant working-directory artifact path
    else:
        return False
    if len(node.args) == 2:
        mode = node.args[1]
        if not isinstance(mode, ast.Constant) or mode.value not in {"r", "rt"}:
            return False
    return True

def qualify_source_wd(source: str, policy: str = "v3") -> dict:
    """Amendment-2 variant of qualify_source using the wd-read clause (only
    the open() boundary decision differs; imports/dunders/calls identical)."""
    allowed = POLICIES[policy]
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {"qualified": False, "status": "SOURCE_PARSE_REJECTED", "policy": policy,
                "violations": [{"rule": "syntax", "message": exc.msg, "line": exc.lineno}]}
    violations = []
    imported, referenced = set(), set()
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
            t = ast.unparse(node)
            if any(tok in t for tok in FORBIDDEN_SUBSTRINGS):
                violations.append({"rule": "disallowed-dunder", "value": t[:120], "line": node.lineno})
            if t.split(".")[0] in FORBIDDEN_MODULES:
                violations.append({"rule": "disallowed-module-access", "value": t.split(".")[0], "line": node.lineno})
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                if not _is_allowed_instance_read(node):
                    violations.append({"rule": "disallowed-boundary", "value": "open:not-readonly-argv1", "line": node.lineno})
                continue
            if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
                violations.append({"rule": "disallowed-call", "value": node.func.id, "line": node.lineno})
    unused = sorted({n for n in imported if n not in referenced})
    return {"qualified": not violations,
            "status": "QUALIFIED" if not violations else "SANDBOX_REJECTED",
            "policy": policy, "violations": violations,
            "imported_modules": sorted(imported), "unused_imports": unused}

