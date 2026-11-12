#!/usr/bin/env python3
"""P010 leak scan + integrity snapshot.

1) Leak scan: for every seed 41-44, compute the fixture truth (plaintext hex) and
   the fixture key hex with the SAME derivation as run_code_feedback_chacha20.instance,
   then scan every text-readable file under info_contract_2x2_20261018/ for those
   secrets (raw hex, upper, spaced-pair form). Prompts must contain none.
2) Integrity snapshot: hashes/all_artifacts.sha256 over all files in the dir
   (excluding the snapshot files themselves), plus STATUS_INFO_CONTRACT.json.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_code_feedback_chacha20 import instance  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "info_contract_2x2_20261018"
SEEDS = [41, 42, 43, 44]


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
            "public_input_sha256": hashlib.sha256(json.dumps(public, sort_keys=True).encode()).hexdigest(),
        }

    scans = {}
    hits = []
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(OUT))
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
                      "files_with_hits": len(hits), "prompt_files_with_hits": len(prompt_hits),
                      "leak_free_prompts": result["leak_free_prompts"]}, indent=2))

    # Integrity snapshot (after leak scan so the scan file is hashed too)
    manifest_lines = []
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(OUT))
        if rel in {"hashes/all_artifacts.sha256", "STATUS_INFO_CONTRACT.json", "hashes/manifest.sha256"}:
            continue
        manifest_lines.append(f"{sha256_file(p)}  {rel}")
    (OUT / "hashes").mkdir(exist_ok=True)
    (OUT / "hashes" / "all_artifacts.sha256").write_text("\n".join(manifest_lines) + "\n")

    res = []
    if (OUT / "results.jsonl").exists():
        for line in (OUT / "results.jsonl").read_text().splitlines():
            if line.strip():
                res.append(json.loads(line))
    status = {
        "protocol": "P010-INFO-CONTRACT-2X2-CHACHA20-v1",
        "sessions": len(res),
        "accepted": sum(r.get("status") == "SUCCESS" for r in res),
        "status_counts": {s: sum(r.get("status") == s for r in res) for s in sorted({r.get("status") for r in res})},
        "leak_free_prompts": result["leak_free_prompts"],
        "files_hashed": len(manifest_lines),
        "interpretation": ("Preregistered matched 2x2 information-contract intervention on a local ChaCha20 "
                           "nonce-reuse fixture; mechanism identification only; not a capability rate estimate; "
                           "not pooled with H1 V2, V4, or post-freeze cohorts."),
    }
    (OUT / "STATUS_INFO_CONTRACT.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    print(json.dumps(status, indent=2, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())
