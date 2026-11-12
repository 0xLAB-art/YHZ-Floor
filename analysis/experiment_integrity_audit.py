#!/usr/bin/env python3
"""Read-only corpus audit; never runs agents, exploits, or provider requests."""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "schema"))
from corpus_identity import validate_index
from e4_sensitivity import inadmissible_reason


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def filename_identity(run_id):
    match = re.fullmatch(r"v2_(O\d+)__(.+)__(T\d_[^_]+)__rep(\d+)", run_id)
    return {"slot": match[1], "task": match[2], "track": match[3], "rep": int(match[4])} if match else None


def comparison_scope(defects, tracks, malformed, snapshots, clocks, mixed):
    identity_ok = not defects and not tracks and not malformed
    return {
        "retained_census_only": True,
        "track_comparison_supported": identity_ok and not clocks,
        "frozen_backend_comparison_supported": identity_ok and not snapshots and not clocks and not mixed,
        "semantic_identity_screen_passed": identity_ok and not snapshots and not clocks and not mixed,
        "campaign_population_estimates_authorized": False,
        "boundary": "Screening only; passing cannot establish prospective freeze, planned-cell coverage, or per-request backend provenance.",
    }


def audit_corpus(corpus, scheduled=None):
    index = corpus / "INDEX.jsonl"
    files = sorted(corpus.glob("v2_*.json"))
    snapshots = {str(p): sha(p) for p in files + ([index] if index.exists() else [])}
    rows = [json.loads(line) for line in index.read_text().splitlines() if line.strip()] if index.exists() else []
    indexed = {row.get("run_id") for row in rows}
    physical = set()
    models, tracks, clock_exclusions = defaultdict(Counter), [], Counter()
    missing_snapshots, statuses, malformed = [], Counter(), []
    for path in files:
        record = json.loads(path.read_text())
        run_id = record.get("run_id")
        physical.add(run_id)
        if run_id != path.stem:
            malformed.append(path.name)
        expected = filename_identity(str(run_id))
        card = record.get("task_card") or {}
        config = record.get("model_config") or {}
        slot = expected["slot"] if expected else "unparsed"
        models[slot][(config.get("provider"), config.get("model_id"), config.get("model_snapshot"))] += 1
        snapshot = config.get("model_snapshot") or ""
        if not snapshot or "runtime-override" in snapshot or snapshot.lower() in {"unknown", "unavailable"}:
            missing_snapshots.append(run_id)
        if expected and (card.get("track") or card.get("starting_information")) != expected["track"]:
            tracks.append({"run_id": run_id, "filename_track": expected["track"],
                           "record_track": card.get("track") or card.get("starting_information")})
        statuses[(record.get("session") or {}).get("status")] += 1
        reason = inadmissible_reason(record)
        if reason:
            clock_exclusions[reason] += 1
    defects = validate_index(corpus) if index.exists() else ["no manifest; not a born-valid indexed corpus"]
    mixed = [slot for slot, values in models.items() if len(values) != 1]
    if any(sha(Path(path)) != digest for path, digest in snapshots.items()):
        raise RuntimeError("source evidence changed during audit")
    return {
        "corpus": corpus.name, "source_file_sha256": snapshots,
        "manifest_rows": len(rows), "unique_indexed_ids": len(indexed),
        "physical_records": len(files), "unindexed_physical_ids": sorted(physical - indexed),
        "indexed_missing_physical_ids": sorted(indexed - physical),
        "identity_defects": defects, "filename_record_mismatches": malformed,
        "filename_track_mismatches": tracks,
        "unfrozen_or_missing_snapshot_ids": missing_snapshots,
        "clock_exclusions": dict(clock_exclusions), "physical_status_census": dict(statuses),
        "mixed_configuration_slots": mixed,
        "slot_provenance": {slot: [{"provider": key[0], "model_id": key[1],
                                    "snapshot": key[2], "records": count}
                                   for key, count in values.items()] for slot, values in models.items()},
        "scheduled": scheduled, "scheduled_grid_completed": scheduled is not None and len(indexed) == scheduled,
        "analysis_scope": comparison_scope(defects, tracks, malformed, missing_snapshots, clock_exclusions, mixed),
        "boundary": "Audit-only census and integrity diagnostics, not ASR/FSR/ranking or restored overwritten evidence.",
    }


def audit():
    corpora = [("runs_w2_pilot", 20), ("runs_e2", 270), ("runs_e2_r230", 230),
               ("runs_e2_r230_full_01", 230), ("runs_e2_r230_opencode_01", 230)]
    reports = [audit_corpus(ROOT / "sp2027/agent-eval" / name, count) for name, count in corpora]
    labels = {}
    for path in sorted((ROOT / "sp2027/benchmarks").glob("*/fields.md")):
        labels[path.parent.name] = {"first_pass_ai_label": "AI, first pass" in path.read_text(),
                                    "worksheet_sha256": sha(path)}
    return {"schema": "experiment-integrity-audit/1", "source_preserved": True,
            "corpora": reports, "e1_auditor_source_labels": labels,
            "independent_human_ratings_collected": False,
            "provider_or_target_calls": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit()
    if args.output:
        if args.output.exists():
            raise SystemExit("refusing to overwrite an existing audit")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    for corpus in report["corpora"]:
        print(json.dumps({k: corpus[k] for k in ("corpus", "manifest_rows", "unique_indexed_ids", "physical_records", "clock_exclusions")}
                         | {"identity_defect_count": len(corpus["identity_defects"]),
                            "track_mismatches": len(corpus["filename_track_mismatches"]),
                            "unfrozen_snapshots": len(corpus["unfrozen_or_missing_snapshot_ids"])}))
