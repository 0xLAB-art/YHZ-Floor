#!/usr/bin/env python3
"""Produce a non-destructive audit view of a damaged W3 manifest.

This tool never changes ``INDEX.jsonl`` or a physical session record.  Its
optional outputs are clearly labelled *derived audit artifacts*, not campaign
evidence: a physical record that overwrote an earlier attempt cannot recover
the earlier outcome or make the W3 aggregate valid.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "schema"))
from corpus_identity import (PROJECT_ROOT, record_identity, resolve_transcript,
                             sha256_file, validate_index)  # noqa: E402

DEFAULT_CORPUS = HERE.parent / "agent-eval" / "runs_e2"
DERIVED_DIR = HERE / "reconciliation"


def load_source_rows(index: Path) -> tuple[list[tuple[int, dict]], list[str]]:
    rows, errors = [], []
    for line_no, raw in enumerate(index.read_text().splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON ({exc.msg})")
            continue
        if not isinstance(row, dict) or not isinstance(row.get("run_id"), str):
            errors.append(f"line {line_no}: missing string run_id")
            continue
        rows.append((line_no, row))
    return rows, errors


def reconciled_rows(corpus: Path, source_rows: list[tuple[int, dict]]) -> tuple[list[dict], dict]:
    by_id: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    for item in source_rows:
        by_id[item[1]["run_id"]].append(item)
    rows, orphan_records, invalid_records = [], [], []
    physical_ids = set()
    for path in sorted(corpus.glob("v2_*.json")):
        try:
            record = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            invalid_records.append({"file": path.name, "error": exc.msg})
            continue
        run_id = record.get("run_id")
        if not isinstance(run_id, str) or path.name != f"{run_id}.json":
            invalid_records.append({"file": path.name, "error": "file/run_id mismatch"})
            continue
        physical_ids.add(run_id)
        sources = by_id.get(run_id, [])
        ident = record_identity(record)
        transcript_dir = corpus / "transcripts" / run_id
        try:
            transcript_value = str(transcript_dir.relative_to(PROJECT_ROOT))
        except ValueError:  # permits isolated temporary-corpus regression tests
            transcript_value = str(transcript_dir)
        canonical = {
            "run_id": run_id,
            **ident,
            "transcript": transcript_value,
            "record_sha256": sha256_file(path),
            "source_index_lines": [line for line, _ in sources],
            "reconciliation_state": "DERIVED_AUDIT_ONLY_NOT_ANALYSIS_ELIGIBLE",
        }
        # Carry operational timing only when exactly one manifest row agrees
        # with every record-derived field.  Otherwise it is ambiguous which
        # overwritten execution the timing described.
        if len(sources) == 1 and all(sources[0][1].get(k) == v for k, v in ident.items()):
            for key in ("rep", "wall_s", "utc"):
                if key in sources[0][1]:
                    canonical[key] = sources[0][1][key]
        rows.append(canonical)
    for run_id, sources in by_id.items():
        if run_id not in physical_ids:
            orphan_records.append({"run_id": run_id,
                                   "source_index_lines": [line for line, _ in sources]})
    report = {
        "physical_record_count": len(rows),
        "source_manifest_row_count": len(source_rows),
        "source_unique_run_id_count": len(by_id),
        "duplicate_source_run_ids": {run_id: [line for line, _ in sources]
                                     for run_id, sources in by_id.items() if len(sources) > 1},
        "orphan_manifest_rows": orphan_records,
        "invalid_physical_records": invalid_records,
    }
    return rows, report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", nargs="?", type=Path, default=DEFAULT_CORPUS)
    ap.add_argument("--write-derived", action="store_true",
                    help="write INDEX_RECONCILED.jsonl and RECONCILIATION_REPORT.json; raw evidence remains untouched")
    args = ap.parse_args()
    corpus = args.corpus.resolve()
    index = corpus / "INDEX.jsonl"
    if not index.exists():
        print(f"missing source manifest: {index}")
        return 2
    source_rows, parse_errors = load_source_rows(index)
    rows, report = reconciled_rows(corpus, source_rows)
    defects = validate_index(corpus)
    report.update({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_manifest": str(index),
        "source_identity_defect_count": len(defects),
        "source_identity_defects": defects,
        "source_parse_errors": parse_errors,
        "derived_manifest": str(DERIVED_DIR / f"{corpus.name}_INDEX_RECONCILED.jsonl"),
        "analysis_eligibility": False,
        "disposition": ("The original INDEX.jsonl remains authoritative historical evidence and is invalid for aggregation. "
                        "The derived manifest is an audit inventory of current physical files only; it does not restore overwritten attempts or authorize W3 analysis."),
    })
    print(f"source rows={len(source_rows)}; physical records={len(rows)}; "
          f"identity defects={len(defects)}")
    print("analysis eligibility: NO — reconciliation documents loss; it does not repair it")
    if args.write_derived:
        # Keep non-session JSON outside the corpus. acts_audit deliberately
        # scans every top-level *.json there, so a report beside run records
        # would be misclassified as a malformed session.
        DERIVED_DIR.mkdir(parents=True, exist_ok=True)
        derived = DERIVED_DIR / f"{corpus.name}_INDEX_RECONCILED.jsonl"
        audit = DERIVED_DIR / f"{corpus.name}_RECONCILIATION_REPORT.json"
        if derived.exists() or audit.exists():
            print("refusing to overwrite an existing derived reconciliation artifact")
            return 4
        derived.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")
        audit.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"wrote audit-only artifacts: {derived}, {audit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
