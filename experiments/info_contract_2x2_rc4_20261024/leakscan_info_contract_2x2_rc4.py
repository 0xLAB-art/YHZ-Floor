#!/usr/bin/env python3
"""P011 leak scan + integrity snapshot (structural mirror of
leakscan_info_contract_2x2.py).

1) Leak scan: for each seed 81-84, derive the fixture truth (target plaintext
   hex), the base RC4 key hex, and the effective RC4 key hex (key||nonce) with
   the SAME derivation as rc4_fixture.instance, then scan every text-readable
   file under this namespace for those secrets (raw hex, upper, spaced-pair
   form). Prompt files must contain none. Hits in execution_captures/*.stdout.txt
   are expected only as accepted candidates' own recovered output.
2) Integrity snapshot: hashes/all_artifacts.sha256 over all files in the
   namespace (excluding the manifest container and the files written after
   this scan), plus STATUS_INFO_CONTRACT_RC4.json.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rc4_fixture import NONCE, PROTOCOL, SEEDS, instance  # noqa: E402


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
        key = hashlib.sha256(f"acts-rc4-key-{seed}".encode()).digest()[:16]
        secrets[seed] = {
            "truth_hex": truth.hex(),
            "base_key_hex": key.hex(),
            "effective_key_hex": (key + NONCE).hex(),
            "public_input_sha256": hashlib.sha256(json.dumps(public, sort_keys=True).encode()).hexdigest(),
        }

    scans = {}
    hits = []
    for p in sorted(HERE.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(HERE))
        if rel.startswith("hashes/") or rel == "LEAK_SCAN.json":
            # hashes/ is the manifest container; LEAK_SCAN.json is this scanner's own
            # output and intentionally embeds the secrets_derived block it scans for
            # (P010 precedent). Scanning it would be self-referential.
            continue
        try:
            text = p.read_text(errors="replace")
        except Exception:
            continue
        entry = {"file": rel, "bytes": p.stat().st_size, "hits": []}
        for seed, s in secrets.items():
            for label in ("truth_hex", "base_key_hex", "effective_key_hex"):
                for v in variants(s[label]):
                    if len(v) >= 32 and v in text:
                        entry["hits"].append({"seed": seed, "field": label})
                        break
        scans[rel] = entry
        if entry["hits"]:
            hits.append(entry)

    prompt_files = [r for r in scans if r.startswith("prompts/")]
    prompt_hits = [e for e in hits if e["file"].startswith("prompts/")]
    # Expected, non-leak hit classes (model-invisible, locally derived):
    #  - execution_captures/*.stdout.txt: the accepted candidates' own oracle-verified
    #    recovered output (same classification as P010).
    #  - preflight/ambiguity_witness.json: local preflight underdetermination record;
    #    never visible to the model; the truth is trivially derivable from the public
    #    input under the stated all-zero reference premise.
    expected_hit_files = set()
    for e in hits:
        if (e["file"].startswith("execution_captures/") and e["file"].endswith(".stdout.txt")
                and {h["field"] for h in e["hits"]} == {"truth_hex"}):
            expected_hit_files.add(e["file"])
        if e["file"] == "preflight/ambiguity_witness.json" \
                and {h["field"] for h in e["hits"]} == {"truth_hex"}:
            expected_hit_files.add(e["file"])
    unexpected_hits = [e for e in hits if e["file"] not in expected_hit_files]
    result = {
        "protocol": PROTOCOL,
        "secrets_derived": secrets,
        "files_scanned": len(scans),
        "prompt_files": len(prompt_files),
        "files_with_hits": hits,
        "prompt_files_with_hits": prompt_hits,
        "leak_free_prompts": len(prompt_hits) == 0,
        "expected_hit_classification": {
            "accepted_stdout_recovered_output_count": sum(1 for f in expected_hit_files if f.startswith("execution_captures/")),
            "preflight_witness_local_record": sorted(f for f in expected_hit_files if f.startswith("preflight/")),
            "note": ("stdout hits are the accepted candidates' own oracle-verified recovered output; the "
                     "witness hit is a local preflight record never visible to the model. Neither is leakage."),
        },
        "unexpected_hits": unexpected_hits,
        "leak_free_overall": len(prompt_hits) == 0 and len(unexpected_hits) == 0,
    }
    (HERE / "LEAK_SCAN.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"files_scanned": len(scans), "prompt_files": len(prompt_files),
                      "files_with_hits": len(hits), "prompt_files_with_hits": len(prompt_hits),
                      "unexpected_hits": len(unexpected_hits),
                      "leak_free_prompts": result["leak_free_prompts"],
                      "leak_free_overall": result["leak_free_overall"]}, indent=2))

    # Integrity snapshot (after leak scan so the scan file is hashed too)
    manifest_lines = []
    for p in sorted(HERE.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(HERE))
        if rel in {"hashes/all_artifacts.sha256", "STATUS_INFO_CONTRACT_RC4.json",
                   "FINAL_FREEZE.json", "hashes/manifest.sha256"}:
            continue
        manifest_lines.append(f"{sha256_file(p)}  {rel}")
    (HERE / "hashes").mkdir(exist_ok=True)
    (HERE / "hashes" / "all_artifacts.sha256").write_text("\n".join(manifest_lines) + "\n")

    res = []
    if (HERE / "results.jsonl").exists():
        for line in (HERE / "results.jsonl").read_text().splitlines():
            if line.strip():
                res.append(json.loads(line))
    status = {
        "protocol": PROTOCOL,
        "sessions": len(res),
        "accepted": sum(r.get("status") == "SUCCESS" for r in res),
        "status_counts": {s: sum(r.get("status") == s for r in res) for s in sorted({r.get("status") for r in res})},
        "leak_free_prompts": result["leak_free_prompts"],
        "leak_free_overall": result["leak_free_overall"],
        "files_hashed": len(manifest_lines),
        "interpretation": ("Preregistered matched 2x2 information-contract intervention on a local RC4 "
                           "keystream-reuse fixture; mechanism identification only; not a capability rate "
                           "estimate; not pooled with P010, H1 V2, V4, or post-freeze cohorts."),
    }
    (HERE / "STATUS_INFO_CONTRACT_RC4.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0 if result["leak_free_overall"] else 1


if __name__ == "__main__":
    sys.exit(main())
