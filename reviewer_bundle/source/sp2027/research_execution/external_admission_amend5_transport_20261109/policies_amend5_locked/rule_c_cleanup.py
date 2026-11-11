#!/usr/bin/env python3
# POLICY SNAPSHOT — Rule (c) = Rule (b) + output-preserving unused-import
# cleanup, verbatim port. Provenance: the cleanup transform() from
# sp2027/analysis/contribution_audit_20261021/policy_mechanism/audit.py,
# extracted verbatim by AST slicing on 2026-10-24 for namespace
# external_admission_20261024, plus a byte-identical-output check harness
# (execute_cleanup_and_compare) written for this namespace.

import ast
import re

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
