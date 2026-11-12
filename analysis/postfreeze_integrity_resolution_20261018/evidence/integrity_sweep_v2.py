#!/usr/bin/env python3
"""Integrity sweep v2 with correct base-directory resolution.

Rule: manifests inside a `hashes/` subdirectory list paths relative to the ATTEMPT ROOT
(parent of `hashes/`); manifests directly inside an attempt dir also list paths relative
to that attempt dir. Absolute entries are used as-is. Annotates:
  - self-referential entries (manifest file listed in itself)
  - empty-file-at-snapshot entries (recorded e3b0c442...)
  - genuinely missing files
  - content mismatches
Run on the live /tmp/opencode/novelty_program tree; hardlink-equivalence with repo copies
is reported separately.
"""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path

ROOT = Path("/tmp/opencode/novelty_program")
EMPTY_SHA = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


manifests = []
for dirpath, _, filenames in os.walk(ROOT):
    for fn in filenames:
        if fn.endswith(".sha256"):
            manifests.append(Path(dirpath) / fn)

results = []
counts = collections.Counter()
per_manifest = []

for man in sorted(manifests):
    real = man.resolve()
    parts = real.parts
    if "hashes" in real.parent.name:
        base = real.parent.parent
    else:
        base = real.parent
    entries, m_counts = [], collections.Counter()
    try:
        lines = real.read_text().splitlines()
    except Exception as e:
        print("UNREADABLE", real, e)
        continue
    seen_files = {}
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        p = ln.split(None, 1)
        if len(p) != 2:
            continue
        rec, rel = p[0], p[1].strip()
        if len(rec) != 64:
            continue
        cand = Path(rel)
        if not cand.is_absolute():
            cand = (base / rel).resolve()
        st = None
        try:
            st = cand.stat()
        except Exception:
            pass
        if not cand.exists():
            act = None
            kind = "MISSING"
        else:
            act = sha(cand)
            if act == rec:
                kind = "MATCH"
            elif rec == EMPTY_SHA:
                kind = "EMPTY_AT_SNAPSHOT"
            elif cand == real:
                kind = "SELF_STALE"
            else:
                kind = "MISMATCH"
        # hardlink-dedup: same inode+hash seen -> skip recount
        key = (st.st_ino, st.st_dev) if st else None
        if key and kind == "MATCH":
            if key in seen_files:
                kind = "MATCH_DUP"
            seen_files[key] = True
        m_counts[kind] += 1
        if kind not in ("MATCH", "MATCH_DUP"):
            entries.append({
                "kind": kind, "recorded": rec, "actual": act,
                "file": str(cand),
                "mtime": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S") if st else None,
                "base": str(base),
            })
    counts.update(m_counts)
    per_manifest.append({"manifest": str(real), "base": str(base), "counts": dict(m_counts), "problems": entries})

print("GLOBAL:", dict(counts))
print()
for pm in per_manifest:
    probs = pm["problems"]
    if probs:
        print(f"== {pm['manifest']} (base {pm['base']})")
        for e in probs:
            print(f"   {e['kind']:18s} {e['file']}")
            if e["kind"] == "MISMATCH":
                print(f"      rec {e['recorded']}")
                print(f"      act {e['actual']}")
                print(f"      mtime {e['mtime']}")
        print()
Path("/tmp/opencode/integrity_sweep_v2.json").write_text(json.dumps({"counts": dict(counts), "per_manifest": per_manifest}, indent=2) + "\n")
print("written /tmp/opencode/integrity_sweep_v2.json")
