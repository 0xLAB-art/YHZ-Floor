#!/usr/bin/env python3
"""P010L3 leak scan + integrity snapshot.

Same logic as sp2027/research_execution/leakscan_info_contract_2x2.py (P010),
adapted to this namespace's seeds (111-118) and output directory:

1) Leak scan: derive the fixture truth (plaintext hex) and key hex for every
   seed 111-118 with the SAME derivation as run_code_feedback_chacha20.instance,
   then scan every text-readable file in this namespace for those secrets
   (raw hex, upper, spaced-pair form). Prompts must contain none.
2) Integrity snapshot: hashes/all_artifacts.sha256 over all files excluding
   the snapshot files themselves.

No subprocess; analysis-only (runs after the cohort is complete).
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0]))  # sp2027/research_execution
from run_code_feedback_chacha20 import instance  # noqa: E402

OUT = HERE
SEEDS = [201, 202, 203, 204, 205, 206, 207, 208]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def variants(hexstr: str):
    spaced = " ".join(hexstr[i:i + 2] for i in range(0, len(hexstr), 2))
    return {hexstr, hexstr.upper(), spaced, spaced.upper()}


def main():
    secrets = {}
    for seed in SEEDS:
        public, truth = instance(seed)
        key = hashlib.sha256(f"acts-chacha20-key-{seed}".encode()).digest()
        secrets[seed] = {
            "truth_hex": truth.hex(),
            "key_hex": key.hex(),
            "public_input_sha256": hashlib.sha256(
                json.dumps(public, sort_keys=True).encode()).hexdigest(),
        }

    scans = {}
    hits = []
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(OUT))
        if rel.startswith(("hashes/", "leakscan_label2.py")):
            continue
        try:
            text = p.read_text(errors="replace")
        except Exception:
            continue
        entry = {"file": rel, "bytes": p.stat().st_size, "hits": []}
        for seed, s in secrets.items():
            for label in ("truth_hex", "key_hex"):
                for v in variants(s[label]):
                    if len(v) >= 32 and v in text:
                        entry["hits"].append({"seed": seed, "field": label})
                        break
        scans[rel] = entry
        if entry["hits"]:
            hits.append(entry)

    prompt_files = [r for r in scans if r.startswith("prompts/")]
    prompt_hits = [e for e in hits if e["file"].startswith("prompts/")]
    result = {
        "secrets_derived": secrets,
        "files_scanned": len(scans),
        "prompt_files": len(prompt_files),
        "files_with_hits": hits,
        "prompt_files_with_hits": prompt_hits,
        "leak_free_prompts": len(prompt_hits) == 0,
    }
    (OUT / "LEAK_SCAN.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"files_scanned": len(scans), "prompt_files": len(prompt_files),
                      "files_with_hits": len(hits),
                      "prompt_files_with_hits": len(prompt_hits),
                      "leak_free_prompts": result["leak_free_prompts"]}, indent=2))

    manifest_lines = []
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(OUT))
        if rel in {"hashes/all_artifacts.sha256"}:
            continue
        manifest_lines.append(f"{sha256_file(p)}  {rel}")
    (OUT / "hashes").mkdir(exist_ok=True)
    (OUT / "hashes" / "all_artifacts.sha256").write_text("\n".join(manifest_lines) + "\n")
    print(f"hashed {len(manifest_lines)} files")


if __name__ == "__main__":
    sys.exit(main())
