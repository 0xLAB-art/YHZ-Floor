#!/usr/bin/env python3
"""Package source references, never first-pass decisions or AI answers."""
import argparse
import hashlib
import json
import random
import re
from pathlib import Path

from build_second_audit_packet import DIRS, FIELDS

ROOT = Path(__file__).resolve().parents[2]


def neutral_sources(text):
    blocks = text.split("```")
    if len(blocks) < 3:
        raise ValueError("worksheet has no source snapshot block")
    snapshot = blocks[1]
    # Deliberately omit the snapshot's prose, which can contain verdicts
    # such as NONE FOUND. Export only literal primary-source identifiers.
    return {"urls": sorted(set(re.findall(r"https?://[^\s`<>]+", snapshot))),
            "commit_hashes": sorted(set(re.findall(r"\b[0-9a-f]{40}\b", snapshot))),
            "arxiv_ids": sorted(set(re.findall(r"arXiv:(\d{4}\.\d{4,5})", snapshot)))}


def build(out):
    if out.exists():
        raise SystemExit("refusing to overwrite a human review packet")
    sources = {}
    inputs = {}
    for benchmark, directory in DIRS.items():
        path = ROOT / "sp2027/benchmarks" / directory / "fields.md"
        sources[directory] = neutral_sources(path.read_text())
        if not sources[directory]["urls"]:
            raise ValueError("primary-source URL missing")
        inputs[directory] = hashlib.sha256(path.read_bytes()).hexdigest()
    order = [f"{directory}::{field}" for directory in DIRS.values() for field in FIELDS]
    random.Random(20261004).shuffle(order)
    out.mkdir(parents=True)
    packet = {"schema": "human-reaudit-packet/1", "seed": 20261004,
              "n_cells": 54, "cells_order": order,
              "fields": {key: {"name": value[0], "question": value[1]} for key, value in FIELDS.items()},
              "primary_sources": sources, "source_snapshot_sha256": inputs,
              "first_pass_values_included": False, "ai_answers_included": False,
              "human_ratings_collected": False,
              "boundary": "Neutral source pointers, not a guarantee of rater blinding or independence."}
    (out / "PACKET.json").write_text(json.dumps(packet, indent=2) + "\n")
    for rater in ("A", "B"):
        rows = "cell_id,rating,evidence_pointer,rationale,judged_utc\n"
        rows += "".join(cell + ",,,,\n" for cell in order)
        (out / f"ratings_{rater}.csv").write_text(rows)
    instructions = """# Independent human re-audit packet — no ratings collected

Use PACKET.json's primary sources and pinned revisions. No first-pass
worksheet, summary table, AI answers, or manuscript findings are included.
Do not open those author-side records before independently committing all
54 decisions. Independent raters must be real humans; AI/model ratings are
not human validation. Record yes/partial/no/opaque, evidence pointer,
rationale, and UTC timestamp for each cell. For F9, yes requires an actual
outcome reconstruction, not merely accessible source code. Missing release
evidence does not establish absence of an internal control. Preserve each
rater's original commitment before comparison and any later adjudication.

Neither a randomized order nor a masked packet proves rater independence.
Disclose prior exposure and other conflicts. Return actual completed ratings
and a human-rater declaration to the coordinator; no recruitment or collection
has been performed in generating this packet.
"""
    (out / "INSTRUCTIONS.md").write_text(instructions)
    inventory = [{"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                 for p in sorted(out.iterdir()) if p.is_file()]
    (out / "MANIFEST.json").write_text(json.dumps({"files": inventory}, indent=2) + "\n")
    print("human packet: 54 masked-source cells; 0 ratings collected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    build(parser.parse_args().output.resolve())
