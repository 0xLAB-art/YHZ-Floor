#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    rows = [json.loads(line) for line in (source / "runs/confirmatory/results.jsonl").read_text().splitlines()]
    if len(rows) != 852 or len({row["session_id"] for row in rows}) != 852:
        raise ValueError("expected 852 unique retained sessions")
    output.mkdir(parents=True, exist_ok=False)
    (output / "code").mkdir()
    for name in ("h1r3_reference.py", "h1r3_contract.py"):
        shutil.copyfile(source / name, output / "code" / name)
    shutil.copyfile(Path(__file__).with_name("replay.py"), output / "replay.py")
    shutil.copyfile(Path(__file__).with_name("REPLAY_README.md"), output / "README.md")
    target = output / "runs/confirmatory"
    target.mkdir(parents=True)
    shutil.copyfile(source / "runs/confirmatory/results.jsonl", target / "results.jsonl")
    file_counts = {}
    for row in rows:
        case = source / "runs/confirmatory/sessions" / row["session_id"]
        dest = target / "sessions" / row["session_id"]
        dest.mkdir(parents=True)
        for item in sorted(case.iterdir()):
            if item.is_file():
                shutil.copyfile(item, dest / item.name)
                file_counts[item.name] = file_counts.get(item.name, 0) + 1
    manifest = {str(path.relative_to(output)): digest(path)
                for path in sorted(output.rglob("*")) if path.is_file()}
    (output / "MANIFEST.json").write_text(json.dumps({
        "schema": "acts-retained-output-replay/1", "sessions": len(rows),
        "scope": "retained-output oracle adjudication; no model or program re-execution",
        "publicly_published": False, "anonymous_release_review_complete": False,
        "files": manifest, "file_counts": file_counts,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"sessions": len(rows), "files": len(manifest), "output": str(output)}))


if __name__ == "__main__":
    main()
