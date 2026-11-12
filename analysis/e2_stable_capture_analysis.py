from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


CONDITIONAL_STATUSES = {
    "SUCCESS",
    "ORACLE_FAIL",
    "TIMEOUT",
    "AGENT_GIVEUP",
    "MODEL_REFUSAL",
    "TOOL_FAILURE",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(successes: int, trials: int, z: float = 1.959963984540054) -> list[float] | None:
    if trials <= 0 or successes < 0 or successes > trials:
        return None
    p = successes / trials
    denominator = 1.0 + z * z / trials
    centre = (p + z * z / (2.0 * trials)) / denominator
    margin = z * ((p * (1.0 - p) / trials + z * z / (4.0 * trials * trials)) ** 0.5) / denominator
    return [centre - margin, centre + margin]


def fraction(successes: int, trials: int) -> dict:
    return {
        "successes": successes,
        "trials": trials,
        "value": successes / trials if trials else None,
        "wilson_95": wilson(successes, trials),
        "label": "descriptive; sessions are clustered by task",
    }


def load(campaign: Path, freeze: Path, out_dir: Path) -> dict:
    manifest = json.loads(campaign.read_text())
    frozen = json.loads(freeze.read_text())
    expected_digest = frozen.get("manifest_sha256")
    actual_digest = sha256(campaign)
    if actual_digest != expected_digest:
        raise SystemExit(f"manifest digest mismatch: {actual_digest} != {expected_digest}")
    if manifest.get("namespace") != manifest.get("qualification_id"):
        raise SystemExit("manifest namespace and qualification_id differ")
    if not manifest["namespace"].startswith("E2-STABLE-CAPTURE-"):
        raise SystemExit("refusing non-stable-capture namespace")

    index_path = out_dir / "INDEX.jsonl"
    rows = [json.loads(line) for line in index_path.read_text().splitlines() if line.strip()]
    by_entry = {row.get("entry_id"): row for row in rows}
    entries = manifest["entries"]
    expected_entries = {entry["entry_id"] for entry in entries}
    if set(by_entry) != expected_entries:
        raise SystemExit(
            f"incomplete or extra schedule: retained={len(by_entry)} expected={len(expected_entries)}"
        )
    if len(rows) != len(by_entry):
        raise SystemExit("duplicate entry_id in INDEX.jsonl")

    records = {}
    for entry in entries:
        record_path = out_dir / f"{by_entry[entry['entry_id']]['run_id']}.json"
        if not record_path.exists():
            raise SystemExit(f"missing retained record for {entry['entry_id']}: {record_path.name}")
        record = json.loads(record_path.read_text())
        if record.get("run_id") != by_entry[entry["entry_id"]].get("run_id"):
            raise SystemExit(f"index/record run_id mismatch for {entry['entry_id']}")
        if record.get("environment", {}).get("qualification", {}).get("namespace") != manifest["namespace"]:
            raise SystemExit(f"record escaped campaign namespace for {entry['entry_id']}")
        records[entry["entry_id"]] = record
    return {"manifest": manifest, "entries": entries, "index": by_entry, "records": records}


def summarize(data: dict) -> dict:
    entries = data["entries"]
    records = data["records"]
    statuses = [records[e["entry_id"]].get("session", {}).get("status") for e in entries]
    successes = sum(status == "SUCCESS" for status in statuses)
    conditional = [status in CONDITIONAL_STATUSES for status in statuses]
    conditional_n = sum(conditional)
    per_task: dict[str, list[str]] = defaultdict(list)
    for entry, status in zip(entries, statuses):
        per_task[entry["task_id"]].append(status)
    return {
        "schema": "e2-stable-capture-analysis/1.0.0",
        "qualification_id": data["manifest"]["qualification_id"],
        "namespace": data["manifest"]["namespace"],
        "scheduled_attempts": len(statuses),
        "status_counts": dict(sorted(Counter(statuses).items())),
        "operational_yield": fraction(successes, len(statuses)),
        "conditional_yield": fraction(successes, conditional_n),
        "conditional_denominator_statuses": sorted(CONDITIONAL_STATUSES),
        "per_task_statuses": {task: values for task, values in sorted(per_task.items())},
        "inference_boundary": "descriptive only; sessions are clustered by task; not pooled with legacy E2",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(load(args.campaign, args.freeze, args.out_dir))
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
