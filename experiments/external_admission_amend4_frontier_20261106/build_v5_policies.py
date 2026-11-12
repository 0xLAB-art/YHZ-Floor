#!/usr/bin/env python3
"""Build the v5 boundary-repair policy modules (Amendment-4c).

v5 = v4 with TWO authority-preserving extensions to the read-boundary clause,
both measured on the frozen Amendment-4 programs before registration:

  (1) read-only opens may carry text-mode keyword parameters
      (encoding/errors/newline/mode) — they change decoding, not access
      authority (60 violating opens: 18 literal + 9 variable with encoding);
  (2) the filename may be a variable statically bound to exactly ONE constant
      bare in-sandbox string (31 violating opens; any reassignment or
      non-constant binding keeps the rejection — conservative residual of 2
      calls stays rejected).

The sys.argv[1] branch keeps v4's exact strictness.  Amend-2 pattern: zero
sessions, zero calls, pre-repair and repaired verdicts both printed.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

HELPER_V4 = '''def _is_allowed_instance_read(node: ast.Call) -> bool:
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
        if not name or "/" in name or "\\\\" in name or name in (".", ".."):
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
    return True'''

HELPER_V5 = '''def _is_allowed_instance_read(node: ast.Call, bindings=None) -> bool:
    """True when the call is a read-only access to the sandboxed instance.

    Amendment 2 adds the literal-filename branch: the sandbox hands the instance
    to external programs as `output.txt` in the working directory, so
    open("output.txt", "r") is the same read authority as open(sys.argv[1], "r").
    Bare names only (no separators, no "."/".."), read-only modes only.

    Amendment 4c (v5) extends the branch two ways, both authority-preserving:
      (1) read-only opens may carry text-mode keyword parameters
          (encoding/errors/newline/mode) -- they change decoding, not access
          authority;
      (2) the filename may be a variable statically bound to exactly one
          constant bare in-sandbox string (single-assignment binding; any
          reassignment or non-constant binding keeps the rejection).
    Registered in PREREGISTRATION_AMEND4C_BOUNDARY_REPAIR.md (Amend-2
    pattern: zero sessions, zero calls, pre-repair and repaired verdicts
    both printed).
    """
    if not isinstance(node.func, ast.Name) or node.func.id != "open":
        return False
    if not node.args or len(node.args) > 2:
        return False
    if any(kw.arg is None for kw in node.keywords):
        return False
    arg = node.args[0]

    resolved = None
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        resolved = arg.value
    elif (bindings is not None and isinstance(arg, ast.Name)
          and isinstance(bindings.get(arg.id), str)):
        resolved = bindings[arg.id]
    if resolved is not None:
        if not resolved or "/" in resolved or "\\\\" in resolved or resolved in (".", ".."):
            return False
        mode_node = node.args[1] if len(node.args) == 2 else None
        for kw in node.keywords:
            if kw.arg == "mode":
                mode_node = kw.value
        if mode_node is not None and not (
                isinstance(mode_node, ast.Constant)
                and mode_node.value in {"r", "rt", "rb"}):
            return False
        for kw in node.keywords:
            if kw.arg not in {"encoding", "errors", "newline", "mode"}:
                return False
            if not isinstance(kw.value, ast.Constant) or not isinstance(kw.value.value, str):
                return False
        return True

    # v4 sys.argv[1] branch: unchanged (v4 keyword strictness preserved here)
    if node.keywords:
        return False
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
    return True'''

CALLSITE_V4 = "if not _is_allowed_instance_read(node):"
CALLSITE_V5 = "if not _is_allowed_instance_read(node, bindings):"

ANCHOR = "    violations: list[dict] = []\n    imported: set[str] = set()"
BINDINGS = '''    # amendment 4c (v5): single-assignment constant-string filename bindings.
    # A name is resolvable only when it has EXACTLY ONE assignment and that
    # assignment is a bare in-sandbox literal; any reassignment, expression
    # binding, or non-bare literal makes it unusable (conservative).
    bindings_raw: dict = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            bindings_raw.setdefault(node.targets[0].id, []).append(node.value)
    bindings: dict = {}
    for tgt, values in bindings_raw.items():
        if len(values) == 1 and isinstance(values[0], ast.Constant) \
                and isinstance(values[0].value, str):
            v = values[0].value
            if v and "/" not in v and "\\\\" not in v and v not in (".", ".."):
                bindings[tgt] = v
            else:
                bindings[tgt] = None
        else:
            bindings[tgt] = None
    violations: list[dict] = []
    imported: set[str] = set()'''

PAIRS = [
    ("policies_amend4/rule_a_permissive_v4.py",
     "policies_amend4/rule_a_permissive_v5.py"),
    ("policies_amend4/rule_b_stress_legacy_repaired.py",
     "policies_amend4/rule_b_stress_legacy_repaired_v5.py"),
]


def main():
    import importlib.util

    for src, dst in PAIRS:
        t = Path(src).read_text()
        assert HELPER_V4 in t, f"helper pattern not found in {src}"
        assert CALLSITE_V4 in t, f"call-site pattern not found in {src}"
        assert ANCHOR in t, f"anchor not found in {src}"
        t = t.replace(HELPER_V4, HELPER_V5)
        t = t.replace(CALLSITE_V4, CALLSITE_V5)
        t = t.replace(ANCHOR, BINDINGS)
        Path(dst).write_text(t)
        print("wrote", dst)

    # sanity battery on the v5 declared policy
    spec = importlib.util.spec_from_file_location("v5a", HERE / PAIRS[0][1])
    v5a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v5a)
    PROG = (
        'import sys\n'
        'filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"\n'
        'with open(filename, "r", encoding="ascii") as f:\n'
        '    bits = "".join(f.read().split())\n'
        'print("x")\n'
    )
    checks = [
        ("variable-bound + encoding-kwarg read QUALIFIES under v5",
         v5a.qualify_source(PROG, "v3")["qualified"] is True),
        ("literal + encoding-kwarg read QUALIFIES under v5",
         v5a.qualify_source('with open("output.txt", "r", encoding="utf-8") as f:\n'
                            '    x = f.read()\n', "v3")["qualified"] is True),
        ("variable-bound 'rb' read QUALIFIES under v5",
         v5a.qualify_source('fn = "ciphertext.txt"\n'
                            'with open(fn, "rb") as f:\n'
                            '    x = f.read()\n', "v3")["qualified"] is True),
        ("write-open still rejected",
         v5a.qualify_source('with open("output.txt", "w") as f:\n    f.write("x")\n',
                            "v3")["qualified"] is False),
        ("write-mode kwarg still rejected",
         v5a.qualify_source('with open("output.txt", mode="w") as f:\n    f.write("x")\n',
                            "v3")["qualified"] is False),
        ("path traversal literal still rejected",
         v5a.qualify_source('with open("../etc/passwd") as f:\n    x=f.read()\n',
                            "v3")["qualified"] is False),
        ("traversal-bound variable still rejected",
         v5a.qualify_source('fn = "../etc/passwd"\nwith open(fn) as f:\n    x=f.read()\n',
                            "v3")["qualified"] is False),
        ("re-assigned variable still rejected",
         v5a.qualify_source('fn = "ciphertext.txt"\nfn = "other.txt"\n'
                            'with open(fn) as f:\n    x=f.read()\n',
                            "v3")["qualified"] is False),
        ("expression-bound variable still rejected",
         v5a.qualify_source('fn = "a" + "b"\nwith open(fn) as f:\n    x=f.read()\n',
                            "v3")["qualified"] is False),
        ("os import still rejected",
         v5a.qualify_source('import os\nprint(os.sep)\n', "v3")["qualified"] is False),
        ("eval still rejected",
         v5a.qualify_source('eval("1+1")\n', "v3")["qualified"] is False),
        ("double-star kwargs rejected",
         v5a.qualify_source('kw={"mode":"r"}\nwith open("output.txt", **kw) as f:\n'
                            '    x=f.read()\n', "v3")["qualified"] is False),
    ]
    ok = True
    for name, passed in checks:
        print(("PASS " if passed else "FAIL ") + name)
        ok = ok and passed
    (HERE / "V5_SANITY_CHECKS.json").write_text(json.dumps(
        {"schema": "external-admission-amend4c-v5-sanity/1",
         "checks": [{"name": n, "passed": p} for n, p in checks],
         "all_passed": ok}, indent=1))
    if not ok:
        raise SystemExit("v5 sanity checks FAILED")
    print("v5 sanity battery: ALL PASS")


if __name__ == "__main__":
    main()
