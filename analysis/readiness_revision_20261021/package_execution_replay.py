#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--retained", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    shutil.copytree(args.retained.resolve(), output / "retained", ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("execute_replay.py", "test_execution_sandbox.py"):
        shutil.copyfile(here / name, output / name)
    shutil.copyfile(here / "EXECUTION_REPLAY_README.md", output / "README.md")
    (output / "validation").mkdir()
    for name in ("retained_output_replay_v2_report.json", "portable_replay_v2_report.json"):
        shutil.copyfile(here / name, output / "validation" / name)
    files = {str(path.relative_to(output)): sha(path) for path in sorted(output.rglob("*")) if path.is_file()}
    (output / "MANIFEST.json").write_text(json.dumps({
        "schema": "acts-complete-program-replay/1", "files": files,
        "scope": "retained-output adjudication and fresh sandboxed program execution",
        "publicly_published": False, "anonymous_release_review_complete": False,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"files": len(files), "output": str(output)}))


if __name__ == "__main__":
    main()
