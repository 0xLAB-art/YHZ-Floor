#!/usr/bin/env python3
"""Project the imported module roots of every H1-R3 candidate program.

The evaluator-policy sensitivity in the manuscript is a counterfactual over
*admission rules*.  To let a reviewer evaluate any such rule offline, this
script projects one fact per session: which standard-library module roots the
generated program imports.  It copies no program text, no prompt, no response
and no target state, and it never calls a provider or re-executes a program.

The import extraction uses the same AST rules as the frozen contract
(h1r3_contract.qualify_source), except that only the module *root* of each
import is recorded.  The contract also records the imported alias name for
``from X import Y`` forms, which mixes names such as ``List`` into the module
set; this projection does not, so a rule can be evaluated over module roots
alone.

Usage:  python3 -B build_import_projection.py [--root <dir>] [--out <file>]
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SESSIONS = "runs/confirmatory/sessions"


def module_roots(source: str) -> list[str]:
    """The distinct module roots the program imports."""
    roots: set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root:
                roots.add(root)
    return sorted(roots)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=HERE,
                    help="the H1-R3 analysis directory")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    root = args.root.resolve()
    out = args.out or (root / "PUBLIC_IMPORT_SETS.json")

    sessions = root / SESSIONS
    if not sessions.is_dir():
        print("missing sessions directory: %s" % sessions)
        return 2

    rows = []
    for d in sorted(sessions.iterdir()):
        if not d.is_dir():
            continue
        cand = d / "candidate.py"
        if not cand.is_file():
            continue
        raw = cand.read_bytes()
        src = raw.decode("utf-8", "replace")
        rows.append({
            "session_id": d.name,
            "imported_modules": module_roots(src),
            "source_sha256": hashlib.sha256(raw).hexdigest(),
        })

    projection = {
        "schema": "h1r3-public-import-sets/1",
        "sessions": len(rows),
        "boundary": (
            "Module roots only, one list per session. No program text, prompt, "
            "response, output or target state is included. The source digest is "
            "the sha256 of the retained candidate program, so a reviewer who "
            "holds the session directories can confirm the projection was "
            "derived from them."
        ),
        "rows": rows,
    }
    out.write_text(json.dumps(projection, indent=1, sort_keys=True) + "\n")

    # A summary a reviewer can read without opening the projection.
    counts: dict[str, int] = {}
    for r in rows:
        for m in r["imported_modules"]:
            counts[m] = counts.get(m, 0) + 1
    summary = {
        "schema": "h1r3-public-import-sets-summary/1",
        "sessions": len(rows),
        "module_root_sessions": dict(sorted(counts.items(), key=lambda kv: -kv[1])),
        "distinct_module_roots": len(counts),
    }
    (out.parent / "DERIVED.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("wrote %s (%d sessions, %d distinct module roots)"
          % (out, len(rows), len(counts)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())