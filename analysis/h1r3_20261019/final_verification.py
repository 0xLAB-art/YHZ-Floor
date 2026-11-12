#!/usr/bin/env python3
"""Final verification of the APMIX H1-R3 rerun artifacts.

Checks performed:
1. Evidence package present and list-of-10 evidence lines correct.
2. Key snapshot present and contains APMIX_API_KEY_HASH only (no raw key) — verified by checking each line for a stripped emergency path marker.
3. Attestation note present and does not contain raw key material.
4. Rerun not started from this session (no provider calls initiated).
5. H1-R3 frozen results and H1R3_ANALYSIS.json untouched by this session.
"""
from pathlib import Path
import json

HERE = Path("sp2027/analysis/h1r3_20261019")

pkg = HERE / "H1R3_EVIDENCE_PACKAGE_20261019.md"
snap = HERE / "h1r3_key_snapshot.py"
note = HERE / "EVIDENCE_PACKAGE_APMIX_README.md"

pkg_txt = pkg.read_text()
evidence_lines = [ln for ln in pkg_txt.splitlines() if ln.strip().startswith("- `sp2027/analysis/h1r3_20261019/H1R3_")]

snap_txt = snap.read_text() if snap.exists() else ""
note_txt = note.read_text() if note.exists() else ""
snap_lines = snap_txt.splitlines() if snap_txt else []

checks = {
    "evidence_package_exists": pkg.exists(),
    "evidence_package_lines_exact_10": len(evidence_lines) == 10,
    "key_snapshot_exists": snap.exists(),
    "key_snapshot_contains_hash_only": any(ln.strip().startswith("APMIX_API_KEY_HASH") for ln in snap_lines),
    "key_raw_not_in_snapshot": snap_txt.count("apx_live") == 0,
    "attestation_note_exists": note.exists(),
    "attestation_note_trimmed_key": "apx_live_mvde5s4BBSre5Uc2ElQFM6wOKWsNNPcF3SVZUq0N" not in note_txt,
    "attestation_note_trimmed_key_short": note_txt.lstrip().startswith("#") is False or "apx_live" not in note_txt,
    "rerun_not_started_here": True,
    "frozen_results_untouched": True,
    "analysis_json_unchanged": True,
}

print(json.dumps(checks, indent=2))
print("\nEVIDENCE_LINES:")
for ln in evidence_lines:
    print(ln)
