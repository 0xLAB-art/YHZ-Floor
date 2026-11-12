#!/usr/bin/env python3
"""CENSUS — Amendment 3 task-pool expansion (NYU CTF Bench, crypto category).

DRAFT 2026-11-05 — offline, $0, zero model calls, zero sessions.
Read-only inspection of the PINNED 2026-10-05 source-freeze archive:

  human_audit/source_freeze_20261005/archives/nyu_ctf_bench__NYU_CTF_Bench__4c5744f55a31.tar.gz
  sha256 ad376a2e1a33856fa3c0b4ac073d921b3337355bf966bd01dfb82a412d41f537
  (recorded by ROOT_COMPLETE_FILESYSTEM_INDEX.csv at source-freeze time;
   re-verify anytime with: sha256sum <archive path>)

Extraction is read-only into a directory OUTSIDE the repository
(/tmp/opencode/nyu_pin/), the same discipline Phase 2 used for the Cybench pin
(/tmp/cybench_pin/).  The archive itself is never modified.

Census mirrors the FROZEN Phase-2 selection rule verbatim
(sp2027/research_execution/external_admission_20261024/PREREGISTRATION.md section 3):

  1. metadata category includes 'crypto';     (challenge.json: category == 'crypto')
  2. final answer is a static deterministic string, exact-match checkable;
     (challenge.json: 'flag' is the pinned answer; our oracle compares the
      submitted line against the pinned flag, native exact-match semantics)
  3. runnable offline in the harness: no external service, no
     service-by-construction challenge, artifacts complete in the release files;
     (challenge.json: box == '' AND no Dockerfile/compose/socat/xinetd/nc/listen
      indicator AND no network import in official solve scripts)
  4. task statement public;                   (challenge.json: 'description' non-empty)
  5. solvable by a program admissible under the frozen declared rule within the
     fixed per-session token budget.
     (PENDING per-task reference-solver verification — the census emits the
      verification worklist; it does NOT mark criterion-5 qualification)

Dispositions the census may emit (criterion 3 only — this census is structural):

  EXTERNAL_SERVICE          box non-empty (the direct analogue of Cybench's target_host)
  SERVICE_BY_CONSTRUCTION   box empty but compose/dockerfile/xinetd/nc-listen
                            indicator, or an official solve script imports
                            socket/urllib/pwn — excluded like Phase 2 excluded
                            diffecient and randsubware
  OFFLINE_CANDIDATE         clear on criteria 1-4; criterion 5 pending per-task
                            offline stdlib-only reference solve

Outputs (same directory, written by this script):
  census_nyu_crypto.json   machine-readable per-challenge census
  CENSUS_TABLE.md          the human census table (all tasks + reasons)
"""

import ast
import json
import re
import sys
from pathlib import Path

EXTRACT_ROOT = Path("/tmp/opencode/nyu_pin")
OUT_DIR = Path(__file__).resolve().parent
SPLITS = ("development", "test")
REMOVED_SPLIT = "removed"
MANIFESTS = {
    "development": EXTRACT_ROOT / "development_dataset.json",
    "test": EXTRACT_ROOT / "test_dataset.json",
}

DOCKER_PATTERN = re.compile(r"(dockerfile|docker-compose|compose\.ya?ml)", re.I)
LISTEN_PATTERN = re.compile(r"\b(socat|xinetd|n?cat)\s+[^\n]*:\d+|\bconnect(?:ion)?\s+(?:to|at)\s+[^\n]*:\d+", re.I)
NETWORK_IMPORTS = {"socket", "ssl", "urllib", "http", "requests", "telnetlib",
                   "ftplib", "smtplib", "urn"}
REMOTE_TOOL_IMPORTS = {"pwn", "pwnlib"}


def stdlib_names():
    names = set(getattr(sys, "stdlib_module_names", ()))  # python >= 3.10
    if not names:  # pragma: no cover
        names = {
            "argparse", "base64", "binascii", "bisect", "builtins", "calendar", "collections",
            "collections.abc", "contextlib", "copy", "csv", "ctypes", "dataclasses", "datetime",
            "decimal", "difflib", "fractions", "functools", "getopt", "getpass", "glob",
            "gzip", "hashlib", "heapq", "hmac", "importlib", "inspect", "io", "itertools",
            "json", "logging", "math", "mimetypes", "operator", "os", "pathlib", "pprint",
            "re", "reprlib", "secrets", "shlex", "shutil", "signal", "stat", "statistics",
            "string", "struct", "subprocess", "sys", "tarfile", "tempfile", "textwrap",
            "threading", "time", "typing", "unicodedata", "unittest", "urllib", "warnings",
            "weakref", "zipfile", "zlib",
        }
    return names


def parse_imports(py_path: Path):
    try:
        src = py_path.read_text(encoding="utf-8", errors="strict")
    except (UnicodeDecodeError, OSError):
        return None  # unparsable source (binary or foreign encoding)
    imports = set()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        for m in re.finditer(
                r"^\s*(?:import|from)\s+([A-Za-z_][A-Za-z0-9_]*)", src, re.M):
            imports.add(m.group(1))
        return imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                imports.add(node.module.split(".")[0])
    return imports


STDLIB = stdlib_names()


def load_manifest(split: str):
    path = MANIFESTS.get(split)
    if not path or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        raise SystemExit(f"manifest unreadable: {path}")
    return data  # id -> {year, event, category, challenge, path}


CRYPTO_CATEGORIES = {"cry", "crypto"}


def is_manifest_crypto(entry) -> bool:
    return (entry.get("category") or "").strip().lower() in CRYPTO_CATEGORIES


def manifest_task_id(split: str, rel_path: str):
    ids = load_manifest(split)
    for tid, entry in ids.items():
        if is_manifest_crypto(entry) and str(entry.get("path")) == rel_path:
            return tid
    return None


def classify_challenge(ch_dir: Path, meta: dict, removed: bool = False):
    files = meta.get("files") or []
    file_hits, file_missing = [], []
    for rel in files:
        p = ch_dir / rel
        (file_hits if p.exists() else file_missing).append(rel)

    py_imports = {}
    for py in sorted(ch_dir.rglob("*.py")):
        got = parse_imports(py)
        if got is not None:
            py_imports[str(py.relative_to(ch_dir))] = got

    compose_hits = [str(p.relative_to(ch_dir)) for p in sorted(ch_dir.rglob("*"))
                    if p.is_file() and DOCKER_PATTERN.search(p.name)]

    readme_listen_hits = []
    readme = ch_dir / "README.md"
    if readme.exists():
        try:
            text = readme.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        for m in re.finditer(
                r"(?i)(\b(?:socat|xinetd)\b|\b(?:nc|ncat)\b[^\n]{0,80}:\d{4,5}\b|"
                r"[\w\.\-]+:\d{4,5}\b)", text):
            readme_listen_hits.append(m.group(0).strip()[:160])
        # dedupe, drop bare clock times / prose (a CTF target is host:4-5-digit-port
        # or an explicit socat/xinetd statement)
        readme_listen_hits = [h for h in readme_listen_hits
                              if re.search(r":\d{4,5}\b", h)]

    network_scripts = sorted(rel for rel, mods in py_imports.items()
                             if set(mods) & (NETWORK_IMPORTS | REMOTE_TOOL_IMPORTS))
    nonstdlib_all = set()
    for mods in py_imports.values():
        nonstdlib_all |= {m for m in mods if m not in STDLIB}
    nonstdlib_all -= set()  # no removals; kept for symmetry with imports bookkeeping

    # FLAG-MATERIAL hygiene (pre-leak-scan, extends the LEAK_SCAN pre-freeze):
    # does any DECLARED handout file contain the pinned flag bytes verbatim?
    import hashlib
    flag_material = {"pinned_flag_sha256": None, "flag_bytes_in_handout": [], "description_contains_flag": False}
    flag_value = (meta.get("flag") or "").strip()
    if flag_value:
        flag_material["pinned_flag_sha256"] = hashlib.sha256(flag_value.encode()).hexdigest()[:16] + "..."
        for rel in file_hits:
            p = ch_dir / rel
            try:
                blob = p.read_bytes()
            except OSError:
                continue
            if flag_value.encode() in blob:
                flag_material["flag_bytes_in_handout"].append(rel)
        if flag_value and flag_value in (meta.get("description") or ""):
            flag_material["description_contains_flag"] = True

    box = (meta.get("box") or "").strip()
    if removed:
        disposition = "BENCHMARK_REMOVED"
        reason = ("benchmark authors removed this challenge (benchmark-internal "
                  "'removed/' tree); member of neither dataset manifest")
    elif box:
        disposition = "EXTERNAL_SERVICE"
        reason = f"box={box!r} (declared network service, analogue of Cybench target_host)"
    elif compose_hits or readme_listen_hits or network_scripts:
        bits = []
        if compose_hits:
            bits.append("compose/dockerfile: " + ",".join(compose_hits[:4]))
        if readme_listen_hits:
            bits.append("listen statement: " + readme_listen_hits[0])
        if network_scripts:
            bits.append("script(s) with network imports: " + ",".join(network_scripts[:4]))
        disposition = "SERVICE_BY_CONSTRUCTION"
        reason = "; ".join(bits)
    else:
        disposition = "OFFLINE_CANDIDATE"
        reason = "box empty; no compose/listen/network-solve indicator"

    criterion5 = "PENDING offline stdlib-only reference solve (pinned flag target)"
    if nonstdlib_all:
        criterion5 = (
            "scripts import non-stdlib modules "
            + ", ".join(sorted(nonstdlib_all))
            + " — criterion-5 reference solve must not import these; unresolved"
        )
    return {
        "disposition": disposition,
        "disposition_reason": reason,
        "files_declared": list(files),
        "files_present": file_hits,
        "files_missing": file_missing,
        "python_imports": {k: sorted(v) for k, v in py_imports.items()},
        "nonstdlib_imports_all": sorted(nonstdlib_all),
        "network_scripts": network_scripts,
        "compose_indicators": compose_hits,
        "readme_listen_hits": readme_listen_hits,
        "flag_material": flag_material,
        "criterion5_status": criterion5,
    }


def main():
    if not EXTRACT_ROOT.exists():
        raise SystemExit(
            f"extraction root {EXTRACT_ROOT} missing; re-extract read-only into /tmp first: "
            "tar -xzf <pinned archive> -C /tmp/opencode/nyu_pin"
        )
    records = []
    scanned_dirs = set()
    for split in SPLITS + (REMOVED_SPLIT,):
        split_root = EXTRACT_ROOT / split
        if not split_root.is_dir():
            continue
        for cj in sorted(split_root.rglob("challenge.json")):
            rel = str(cj.relative_to(EXTRACT_ROOT))
            scanned_dirs.add(rel)
            if cj.is_symlink() and not cj.exists():
                records.append({
                    "dataset_split": split,
                    "manifest_id": None,
                    "manifest_member": False,
                    "path_rel": rel,
                    "disposition": "DANGLING_ARCHIVE_ENTRY",
                    "disposition_reason": (
                        "challenge.json inside the pinned archive is a SYMLINK to the "
                        "benchmark authors' machine (/home/...) and does not resolve — "
                        "an archive-construction artifact of the release itself"),
                })
                continue
            try:
                meta = json.loads(cj.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                records.append({"path_rel": rel,
                                "error": str(exc)})
                continue
            meta_category = (meta.get("category") or "").strip().lower()
            ch_dir = cj.parent
            rel_full = cj.relative_to(EXTRACT_ROOT)
            rel_dir = str(ch_dir.relative_to(EXTRACT_ROOT))
            if "/crypto/" in f"/{rel_dir}/" and meta_category not in ("cry", "crypto"):
                # directory says crypto, metadata says otherwise (Phase-2 precedent:
                # Cybench misc/[Easy] Unbreakable kept with its own category)
                records.append({
                    "dataset_split": split,
                    "manifest_id": None,
                    "manifest_member": False,
                    "path_rel": rel_dir,
                    "year": rel_full.parts[1],
                    "event": rel_full.parts[2],
                    "name": meta.get("name"),
                    "metadata_category": meta_category,
                    "disposition": "EXCLUDED_BY_CRITERION_1",
                    "disposition_reason": (
                        f"directory path says crypto but metadata category is "
                        f"'{meta_category}' — Phase-2 rule reads the METADATA "
                        f"(criterion 1), same treatment as Cybench's misc Unbreakable"),
                })
                continue
            if meta_category not in ("cry", "crypto"):
                continue
            got = classify_challenge(ch_dir, meta, removed=(split == REMOVED_SPLIT))
            manifest_id = manifest_task_id(split, rel_dir)
            records.append({
                "dataset_split": split,
                "manifest_id": manifest_id,
                "manifest_member": manifest_id is not None or split == REMOVED_SPLIT,
                "path_rel": rel_dir,
                "year": rel_full.parts[1],
                "event": rel_full.parts[2],
                "name": meta.get("name"),
                "points": meta.get("points"),
                "box": (meta.get("box") or "").strip(),
                "description_present": bool((meta.get("description") or "").strip()),
                "pinned_flag_present": bool((meta.get("flag") or "").strip()),
                **got,
            })

    # reconciliation against the benchmark's own dataset manifests
    reconciliation = {}
    for split in SPLITS:
        manifest = load_manifest(split)
        manifest_cry = {tid for tid, entry in manifest.items()
                        if is_manifest_crypto(entry)}
        manifest_paths = {str(e.get("path")) for e in manifest.values()
                          if is_manifest_crypto(e)}
        census_paths = {r["path_rel"] for r in records if r["dataset_split"] == split}
        reconciliation[split] = {
            "manifest_crypto_tasks": len(manifest_cry),
            "census_rows": len(census_paths),
            "in_manifest_missing_from_census": sorted(manifest_paths - census_paths),
            "in_census_missing_from_manifest": sorted(census_paths - manifest_paths),
        }

    counts = {}
    for r in records:
        counts[r["disposition"]] = counts.get(r["disposition"], 0) + 1
    totals = {
        "pinned_archive": "nyu_ctf_bench__NYU_CTF_Bench__4c5744f55a31.tar.gz",
        "pinned_archive_sha256":
            "ad376a2e1a33856fa3c0b4ac073d921b3337355bf966bd01dfb82a412d41f537",
        "extraction_root": str(EXTRACT_ROOT),
        "extraction_read_only": True,
        "crypto_challenges_total": len(records),
        "disposition_counts": counts,
        "offline_candidates": sum(
            1 for r in records if r["disposition"] == "OFFLINE_CANDIDATE"),
        "flag_asserted_total": sum(
            1 for r in records if r.get("pinned_flag_present")),
        "manifest_member_admitted_rows": sum(
            1 for r in records
            if r.get("manifest_member") and "criterion5_status" in r),
        "splits": {s: sum(1 for r in records if r["dataset_split"] == s)
                   for s in SPLITS + (REMOVED_SPLIT,)},
        "criterion5_outcomes_record": (
            "criterion5_outcomes.json (same namespace directory; executed "
            "offline 2026-11-05 — this census file is the structural "
            "criterion-1..4 record only)"),
        "manifest_reconciliation": reconciliation,
        "accounting_rule": (
            "every challenge.json under crypto directories gets a row: read admitted "
            "(OFFLINE_CANDIDATE / EXTERNAL_SERVICE / SERVICE_BY_CONSTRUCTION / "
            "BENCHMARK_REMOVED), read non-crypto-metadata (EXCLUDED_BY_CRITERION_1), "
            "or unreadable symlink (DANGLING_ARCHIVE_ENTRY) — nothing silently dropped"),
    }
    payload = {"schema": "external-admission-amend3-nyu-census/1-draft",
               **totals, "records": records}
    out_json = OUT_DIR / "census_nyu_crypto.json"
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                        encoding="utf-8")

    lines = [
        "# CENSUS (DRAFT) — NYU CTF Bench crypto category, pinned 2026-10-05 archive",
        "",
        "(Produced by `census_cryptocat.py` under the FROZEN Phase-2 selection rule; "
        "criterion 5 is pending per-task reference solves.)",
        "",
        "Archive sha256 "
        "`ad376a2e1a33856fa3c0b4ac073d921b3337355bf966bd01dfb82a412d41f537`; "
        "extraction read-only into `/tmp/opencode/nyu_pin` (outside the repository).",
        "",
        "| # | split | year/event | task | box | files | disposition | reason / criterion-5 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(records, 1):
        nf, nm = len(r.get("files_present", [])), len(r.get("files_missing", []))
        reason = r.get("disposition_reason", r.get("error", ""))
        c5 = r.get("criterion5_status", "")
        if c5.startswith("scripts import"):
            reason = reason + " ; " + c5
        lines.append(
            f"| {i} | {r['dataset_split']} | {r.get('year', '-')}/{r.get('event', '-')} | "
            f"{r.get('name', '(unreadable)')} "
            f"| {r.get('box') or '-'} | {nf} ok/{nm} missing | {r['disposition']} | {reason} |"
        )
    lines += [
        "",
        f"Totals: {totals['crypto_challenges_total']} crypto challenges "
        f"(development {totals['splits']['development']}, "
        f"test {totals['splits']['test']}, removed {totals['splits']['removed']}); "
        f"OFFLINE_CANDIDATE: {totals['offline_candidates']}; "
        f"EXTERNAL_SERVICE: {counts.get('EXTERNAL_SERVICE', 0)}; "
        f"SERVICE_BY_CONSTRUCTION: {counts.get('SERVICE_BY_CONSTRUCTION', 0)}; "
        f"BENCHMARK_REMOVED: {counts.get('BENCHMARK_REMOVED', 0)}.",
        "",
        "Manifest reconciliation (benchmark's own development/test manifests):",
    ]
    for split, rec in reconciliation.items():
        lines.append(
            f"- {split}: manifest crypto tasks {rec['manifest_crypto_tasks']}, "
            f"census rows {rec['census_rows']}, "
            f"manifest-only {len(rec['in_manifest_missing_from_census'])}, "
            f"census-only {len(rec['in_census_missing_from_manifest'])}"
        )
    lines += [
        "",
        "Boundary: structural census only (criteria 1-4). Criterion 5 is "
        "recorded separately in criterion5_outcomes.json (executed 2026-11-05, "
        "offline). DRAFT status: produced before freeze; no amendment is "
        "registered by this file alone.",
    ]
    (OUT_DIR / "CENSUS_TABLE.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
