import argparse
import hashlib
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[3]
ARCHIVES = ROOT / "human_audit/source_freeze_20261005/archives"
SOURCES = {
    "cybench": (
        "cybench__cybench__ca483c6443f1.tar.gz",
        ("README.md", "agent/agent.py", "grading/unguided_run.py"),
    ),
    "cve_bench": (
        "cve_bench__cve-bench__9fb3e068f260.tar.gz",
        ("README.md", "src/cvebench/cvebench.py", "src/cvebench/prompts.py"),
    ),
}
TERMS = ("allowlist", "allowed_import", "qualify_source", "timeout", "sandbox", "scorer")


def inspect_archive(name, archive_name, requested):
    path = ARCHIVES / archive_name
    result = {
        "benchmark": name,
        "archive": str(path.relative_to(ROOT)),
        "execution": "none; source inventory only",
        "replication_status": "NOT_RUN",
        "entrypoints": [],
    }
    with path.open("rb") as handle:
        result["sha256"] = hashlib.file_digest(handle, "sha256").hexdigest()
    with tarfile.open(path) as archive:
        members = [m for m in archive.getmembers() if m.isfile()]
        result["regular_files"] = len(members)
        for suffix in requested:
            matches = [m for m in members if m.name == suffix]
            if not matches:
                matches = [m for m in members if m.name.endswith("/" + suffix)]
            if len(matches) != 1:
                result["entrypoints"].append({"requested": suffix, "matches": len(matches)})
                continue
            member = matches[0]
            content = archive.extractfile(member).read()
            lines = content.decode("utf-8", errors="replace").splitlines()
            result["entrypoints"].append({
                "path": member.name,
                "sha256": hashlib.sha256(content).hexdigest(),
                "lines": len(lines),
                "relevant_lines": [
                    {"line": i, "text": line.strip()}
                    for i, line in enumerate(lines, 1)
                    if any(term in line.lower() for term in TERMS)
                ],
            })
        result["log_path_members"] = [
            m.name for m in members
            if any(part in {"logs", "trajectories"} for part in Path(m.name).parts)
        ]
    result["boundary"] = (
        "Path/keyword inventory is not proof of missing policy or missing public traces; "
        "external releases may provide separate logs. No admission effect was measured."
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "schema": "acts-external-source-preflight/1",
        "benchmarks": [inspect_archive(k, *v) for k, v in SOURCES.items()],
    }
    body = json.dumps(report, indent=2) + "\n"
    if args.output:
        with args.output.open("x") as handle:
            handle.write(body)
    else:
        print(body, end="")


if __name__ == "__main__":
    main()
