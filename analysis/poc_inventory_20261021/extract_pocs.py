#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[3]
DEST = Path(__file__).resolve().parent / "extracted_recursive_v3"
ROOT_NAMES = (
    "ACTS-ATTACK",
    "agent-eval",
    "analysis",
    "artifact",
    "artifacts",
    "evaluations",
    "extracted",
    "frozen_snapshots",
    "human_audit",
    "human_reaudit",
    "inventory_export_20261018T083057Z",
    "inventory_export_20261018T083537Z_v2",
    "inventory_export_20261018T083537Z_v3",
    "inventory_export_20261018T083537Z_v4",
    "inventory_export_20261018T085024Z_v5",
    "inventory_export_20261018T091940Z_v6_literal",
    "sp2027/agent-eval",
    "sp2027/analysis",
    "sp2027/research_execution",
)
SOURCE_ROOTS = tuple(ROOT / name for name in ROOT_NAMES)
POC_NAMES = {"candidate.py", "program_source.py", "e5_attack_code.py"}
POC_SUFFIX = re.compile(r"\.agent\.py$", re.IGNORECASE)
PATH_KEY = re.compile(r"(candidate|program|exploit|attack).*?(path|file)|(?:path|file).*?(candidate|program|exploit|attack)", re.I)
CODE_KEY = re.compile(r"^(code|candidate_code|program_source|source_code|exploit_code|attack_code|python_code|script)$", re.I)
FENCE = re.compile(r"```(python|py|json)?\s*\n(.*?)```", re.I | re.S)
CODE_MARKER = re.compile(r"(?m)^\s*(?:from\s+[\w.]+\s+import\s+|import\s+[\w.*]+|def\s+\w+\s*\(|async\s+def\s+\w+|class\s+\w+\s*[:(]|#!.*python)|\bsys\.stdin\b|\bsubprocess\.")
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "site-packages", "node_modules"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_files(base: Path):
    for current, dirs, files in os.walk(base, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            yield Path(current) / name


def collect_named_sources() -> dict[Path, set[str]]:
    found: dict[Path, set[str]] = {}
    for base in SOURCE_ROOTS:
        if not base.is_dir():
            continue
        for path in walk_files(base):
            if path.name in POC_NAMES or POC_SUFFIX.search(path.name):
                found.setdefault(path.resolve(), set()).add("filename_signature")
    return found


def collect_referenced_sources(found: dict[Path, set[str]]) -> tuple[int, int, list[dict[str, str]]]:
    scanned = malformed = 0
    embedded: list[dict[str, str]] = []

    def maybe_add_code(source: Path, locator: str, value: str, method: str):
        code = value.strip()
        if len(code) > 20 and CODE_MARKER.search(code):
            embedded.append({"source": source.relative_to(ROOT).as_posix(), "locator": locator, "code": code, "method": method})

    def visit(value, source: Path, locator="#"):
        nonlocal malformed
        if isinstance(value, dict):
            for child_key, child in value.items():
                child_locator = locator + "/" + str(child_key).replace("~", "~0").replace("/", "~1")
                if isinstance(child, str) and PATH_KEY.search(child_key):
                    candidate = Path(child)
                    choices = [candidate] if candidate.is_absolute() else [ROOT / candidate]
                    choices += [base / candidate for base in SOURCE_ROOTS if not candidate.is_absolute()]
                    for choice in choices:
                        try:
                            resolved = choice.resolve(strict=True)
                        except (OSError, RuntimeError):
                            continue
                        if resolved.is_file() and resolved.suffix.lower() in {".py", ".c", ".rs", ".go", ".js", ".java"}:
                            found.setdefault(resolved, set()).add("record_path:" + child_key)
                            break
                if isinstance(child, str) and CODE_KEY.fullmatch(child_key):
                    maybe_add_code(source, child_locator, child, "embedded_code:" + child_key)
                visit(child, source, child_locator)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, source, locator + "/" + str(index))
        elif isinstance(value, str):
            for index, match in enumerate(FENCE.finditer(value)):
                language, body = match.group(1), match.group(2).strip()
                fence_locator = f"{locator}/fence/{index}"
                if language and language.lower() in {"py", "python"}:
                    maybe_add_code(source, fence_locator, body, "python_fence")
                elif language and language.lower() == "json":
                    try:
                        visit(json.loads(body), source, fence_locator + "/json")
                    except json.JSONDecodeError:
                        malformed += 1

    for base in SOURCE_ROOTS:
        if not base.is_dir():
            continue
        for path in walk_files(base):
            if path.suffix.lower() not in {".json", ".jsonl"}:
                continue
            try:
                with path.open("r", encoding="utf-8") as stream:
                    if path.suffix.lower() == ".jsonl":
                        for line in stream:
                            if not line.strip():
                                continue
                            scanned += 1
                            try:
                                visit(json.loads(line), path, f"line/{scanned}")
                            except json.JSONDecodeError:
                                malformed += 1
                    else:
                        scanned += 1
                        visit(json.load(stream), path)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                malformed += 1
    return scanned, malformed, embedded


def main() -> int:
    if DEST.exists():
        print(f"Refusing to overwrite existing output: {DEST}", file=sys.stderr)
        return 2
    found = collect_named_sources()
    scanned, malformed, embedded = collect_referenced_sources(found)
    usable = []
    missing = []
    for path, methods in sorted(found.items(), key=lambda row: str(row[0])):
        try:
            digest = sha256(path)
            size = path.stat().st_size
        except OSError as exc:
            missing.append({"source": str(path), "error": str(exc)})
            continue
        usable.append((path, methods, digest, size))

    DEST.mkdir(parents=True, exist_ok=False)
    objects = DEST / "objects"
    objects.mkdir()
    manifest_path = DEST / "manifest.csv"
    digest_dest: dict[str, str] = {}
    with manifest_path.open("x", newline="", encoding="utf-8") as stream:
        columns = ["source_path", "source_root", "discovery_methods", "sha256", "bytes", "object_path", "duplicate_content"]
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for path, methods, digest, size in usable:
            relative = path.relative_to(ROOT).as_posix()
            object_name = digest + path.suffix.lower()
            target = objects / object_name
            duplicate = digest in digest_dest
            if not duplicate:
                shutil.copyfile(path, target)
                digest_dest[digest] = target.relative_to(DEST).as_posix()
            root_label = next((base.relative_to(ROOT).as_posix() for base in SOURCE_ROOTS if path.is_relative_to(base)), "outside_scanned_roots")
            writer.writerow({
                "source_path": relative,
                "source_root": root_label,
                "discovery_methods": ";".join(sorted(methods)),
                "sha256": digest,
                "bytes": size,
                "object_path": digest_dest[digest],
                "duplicate_content": str(duplicate).lower(),
            })
        for item in embedded:
            code_bytes = item["code"].encode("utf-8")
            digest = hashlib.sha256(code_bytes).hexdigest()
            object_name = digest + ".py"
            target = objects / object_name
            duplicate = digest in digest_dest
            if not duplicate:
                target.write_bytes(code_bytes)
                digest_dest[digest] = target.relative_to(DEST).as_posix()
            source_file = item["source"]
            root_label = next((base.relative_to(ROOT).as_posix() for base in SOURCE_ROOTS if (ROOT / source_file).is_relative_to(base)), "outside_scanned_roots")
            writer.writerow({
                "source_path": source_file + "::" + item["locator"],
                "source_root": root_label,
                "discovery_methods": item["method"],
                "sha256": digest,
                "bytes": len(code_bytes),
                "object_path": digest_dest[digest],
                "duplicate_content": str(duplicate).lower(),
            })

    summary = {
        "schema": "acts-poc-inventory/1",
        "scope": [p.relative_to(ROOT).as_posix() for p in SOURCE_ROOTS if p.is_dir()],
        "recursive": True,
        "source_occurrences": len(usable),
        "embedded_code_occurrences": len(embedded),
        "total_source_occurrences_in_manifest": len(usable) + len(embedded),
        "unique_sha256_objects": len(digest_dest),
        "duplicate_source_occurrences": len(usable) + len(embedded) - len(digest_dest),
        "json_or_jsonl_records_scanned": scanned,
        "malformed_json_records_or_fenced_blocks": malformed,
        "unreadable_poc_sources": missing,
        "execution_performed": False,
        "extraction_rules": {
            "filenames": sorted(POC_NAMES) + ["*.agent.py"],
            "record_path_keys": PATH_KEY.pattern,
            "source_extensions": [".py", ".c", ".rs", ".go", ".js", ".java"],
            "excluded_directories": sorted(SKIP_DIRS),
        },
        "limits": [
            "Unlabeled or unfenced code embedded in free-form text is not independently inferred; structured code fields and Python or JSON fenced blocks in JSON/JSONL records are included.",
            "Presence in this inventory does not mean the program is a valid PoC, was executed, or succeeded.",
            "Source records and duplicate experiment copies remain distinct manifest rows; identical bytes share one stored object.",
        ],
    }
    with (DEST / "SUMMARY.json").open("x", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({k: summary[k] for k in ("source_occurrences", "embedded_code_occurrences", "total_source_occurrences_in_manifest", "unique_sha256_objects", "duplicate_source_occurrences", "json_or_jsonl_records_scanned", "malformed_json_records_or_fenced_blocks", "execution_performed")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
