#!/usr/bin/env python3
"""Build the portable archive-pin manifest for the source_pinning claim.

WHY THIS EXISTS
---------------
`claim_source_pinning` verifies that every pinned benchmark source is present
on disk at its recorded SHA-256. The archives total ~3.0 GB, so the portable
reviewer bundle cannot ship them (the bundle is ~13 MB). Without help, the
portable replay of that claim can only FAIL, which would misrepresent a
correctly-pinned workspace.

WHAT THIS DOES
--------------
It emits a small `ARCHIVE_PINS.json` recording, for each pinned row, the
relative path, the recorded SHA-256, the byte size and a declared basis. The
claim then has three honest outcomes:

  * archives present  -> verify real bytes against the recorded digests
                         (workspace / full replay; unchanged behaviour)
  * archives absent   -> verify MANIFEST integrity and report the claim as
                         "pin list distributed, bytes not shipped"
                         (portable replay) instead of a false failure
  * archives present but digest mismatched -> hard FAIL, as today

The manifest is itself hash-covered by PACKAGE_MANIFEST.json, so a reviewer
can detect edits to the pin list without holding 3 GB.

Nothing here weakens the workspace check: when the archives exist, the real
bytes are still hashed and compared.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]   # .../sp2027/analysis/x.py -> repo root
FREEZE_REL = "human_audit/source_freeze_20261005/SOURCE_FREEZE_20261005_v2.csv"
PINNED_BASES = ("VERIFIED", "PINNED_INFERRED")
MANIFEST_NAME = "ARCHIVE_PINS.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build(freeze_rel: str = FREEZE_REL) -> dict:
    freeze = ROOT / freeze_rel
    rows = list(csv.DictReader(freeze.open(newline="")))
    entries = []
    for row in rows:
        basis = row.get("availability", "")
        if basis not in PINNED_BASES:
            continue
        rel = row["relative_source_path"]
        # The CSV stores paths relative to human_audit/; normalise to repo root.
        repo_rel = f"human_audit/{rel}" if not rel.startswith("human_audit/") else rel
        full = ROOT / repo_rel
        entry = {
            "benchmark": row.get("benchmark"),
            "path": repo_rel,
            "source_url": row.get("source_url"),
            "basis": basis,
            "recorded_sha256": row.get("source_sha256") or None,
            "bytes": None,
            "computed_sha256": None,
            "status": "ABSENT",
        }
        if full.is_file():
            entry["bytes"] = full.stat().st_size
            entry["computed_sha256"] = sha256_file(full)
            entry["status"] = ("VERIFIED"
                               if entry["recorded_sha256"]
                               and entry["computed_sha256"] == entry["recorded_sha256"]
                               else "DIGEST_MISMATCH")
        entries.append(entry)
    return {
        "schema": "archive-pins/1.0",
        "source_freeze": freeze_rel,
        "note": ("Digest-and-size manifest for pinned benchmark sources. The "
                 "archives themselves are ~3.0 GB and are NOT distributed in "
                 "the portable bundle; this manifest lets a reviewer verify the "
                 "pin list and its integrity without the bytes."),
        "entries": entries,
        "summary": {
            "pinned_rows": len(entries),
            "verified": sum(1 for e in entries if e["status"] == "VERIFIED"),
            "digest_mismatch": sum(1 for e in entries if e["status"] == "DIGEST_MISMATCH"),
            "absent": sum(1 for e in entries if e["status"] == "ABSENT"),
            "total_bytes": sum(e["bytes"] or 0 for e in entries),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--freeze", default=FREEZE_REL)
    args = ap.parse_args()
    data = build(args.freeze)
    out = args.out or (ROOT / "human_audit/source_freeze_20261005" / MANIFEST_NAME)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n")
    s = data["summary"]
    print(f"wrote {out.relative_to(ROOT)}: {s['pinned_rows']} pinned rows, "
          f"{s['verified']} verified, {s['digest_mismatch']} mismatch, "
          f"{s['absent']} absent, {s['total_bytes']/1e6:.1f} MB")
    return 1 if s["digest_mismatch"] else 0


if __name__ == "__main__":
    raise SystemExit(main())