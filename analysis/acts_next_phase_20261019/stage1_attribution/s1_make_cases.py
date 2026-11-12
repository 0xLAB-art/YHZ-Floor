#!/usr/bin/env python3
"""Materialise the frozen Stage 1 case inventory.

Run **before** the freeze.  It writes, for every case in the frozen table:

    s1_case_inventory/cases/<case_id>/candidate.py           the program the
                                                                 case executes
    s1_case_inventory/cases/<case_id>/public_instance.json   the public
                                                                 instance the
                                                                 program is
                                                                 given
    s1_case_inventory/cases/<case_id>/alt_candidate.py       (C02 only) the
                                                                 alternative
                                                                 program the
                                                                 case presents
    s1_case_inventory/cases/<case_id>/alt_correct_candidate.py (C03 only) the
                                                                 program whose
                                                                 output the
                                                                 case
                                                                 substitutes

and the frozen case table:

    s1_case_manifest.json

The runner reads the program and the instance from this inventory, so the
confirmatory run cannot drift away from the frozen bytes.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from s1_cases import CASE_SPECS, build_program_source, manifest_document  # noqa: E402
from s1_common import load_frozen_fixture_generator, write_json  # noqa: E402

STAGE1_ROOT = Path(__file__).resolve().parent
INVENTORY_ROOT = STAGE1_ROOT / "s1_case_inventory"
MANIFEST_PATH = STAGE1_ROOT / "s1_case_manifest.json"

# Which auxiliary program each case needs, and which template it is.
AUX_PROGRAMS = {
    "C02_credited_program_not_executed": {"alt_candidate.py": "ecdsa_wrong"},
    "C03_submitted_output_not_observed": {"alt_correct_candidate.py": "ecdsa_correct"},
}


def fixture_for(seed: str, primitive: str):
    fx = load_frozen_fixture_generator()
    if primitive == "ECDSA_Nonce_Reuse":
        return fx.make_ecdsa(seed)
    if primitive == "ChaCha20_Nonce_Repeat":
        return fx.make_chacha(seed)
    raise ValueError(f"unknown primitive {primitive}")


def main() -> int:
    if INVENTORY_ROOT.exists():
        shutil.rmtree(INVENTORY_ROOT)
    (INVENTORY_ROOT / "cases").mkdir(parents=True, exist_ok=True)

    written = 0
    for spec in CASE_SPECS:
        case_dir = INVENTORY_ROOT / "cases" / spec.case_id
        case_dir.mkdir(parents=True, exist_ok=True)

        fixture = fixture_for(spec.seed, spec.primitive)
        instance = fixture[spec.condition.lower()]  # "c1" or "c0"

        source = build_program_source(spec.program, instance, spec.primitive)
        (case_dir / "candidate.py").write_text(source)
        write_json(case_dir / "public_instance.json", instance)
        written += 2

        for filename, template in AUX_PROGRAMS.get(spec.case_id, {}).items():
            (case_dir / filename).write_text(
                build_program_source(template, instance, spec.primitive)
            )
            written += 1

    write_json(MANIFEST_PATH, manifest_document())

    print(json.dumps({
        "case_count": len(CASE_SPECS),
        "inventory_files": written,
        "inventory_root": str(INVENTORY_ROOT.relative_to(STAGE1_ROOT.parents[2])),
        "manifest": str(MANIFEST_PATH.relative_to(STAGE1_ROOT.parents[2])),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
