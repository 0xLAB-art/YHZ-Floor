#!/usr/bin/env python3
"""P012 ECDSA leak scan.

For every seed 141-156, compute the fixture truth (private key hex) with the
SAME derivation as run_info_contract_2x2_ecdsa.instance, then scan every
text-readable file under this namespace (except execution_captures, by
design — accepted-program stdout may echo the recovered secret — and except
the scanner's own outputs) for those secrets in raw/lower/upper/spaced
forms. Prompts must contain none. Writes LEAK_SCAN.json.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from run_info_contract_2x2_ecdsa import instance  # noqa: E402

HERE = Path(__file__).resolve().parent
SEEDS = list(range(141, 157))


def variants(hexstr: str):
    spaced = " ".join(hexstr[i:i + 2] for i in range(0, len(hexstr), 2))
    return {hexstr, hexstr.upper(), spaced, spaced.upper()}


def main():
    secrets = {}
    for seed in SEEDS:
        public, truth = instance(seed)
        secrets[seed] = {
            "truth_hex": f"{truth:064x}",
            "public_input_sha256": hashlib.sha256(json.dumps(public, sort_keys=True).encode()).hexdigest(),
        }

    prompt_hits, prompt_hit_detail, prompt_files = 0, [], 0
    for p in sorted((HERE / "prompts").glob("*.txt")):
        prompt_files += 1
        text = p.read_text(errors="replace")
        for seed, s in secrets.items():
            for form in variants(s["truth_hex"]):
                if form and form in text:
                    prompt_hits += 1
                    prompt_hit_detail.append({"file": p.name, "seed": seed, "form": "truth"})
                    break

    other_hits, other_hit_detail = 0, []
    skip = {"LEAK_SCAN.json", "all_artifacts.sha256", "STATUS_ECCDSA.json"}
    for p in sorted(HERE.rglob("*")):
        if not p.is_file() or p.name in skip:
            continue
        if "execution_captures" in p.parts or "prompts" in p.parts:
            continue
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        for seed, s in secrets.items():
            for form in variants(s["truth_hex"]):
                if form and form in text:
                    other_hits += 1
                    other_hit_detail.append({"file": str(p.relative_to(HERE)), "seed": seed})
                    break

    verdict = "PASS" if prompt_hits == 0 else "FAIL"
    out = {
        "schema": "infoc-ecdsa-leakscan/1",
        "protocol": "P012-INFO-CONTRACT-2X2-ECDSA-NONCE-REUSE-v1",
        "seeds": SEEDS,
        "prompt_files": prompt_files,
        "prompt_hits": prompt_hits,
        "prompt_hit_detail": prompt_hit_detail,
        "other_json_hits": other_hits,
        "other_json_hit_detail": other_hit_detail,
        "verdict": verdict,
        "note": "execution_captures excluded by design (accepted-program stdout may echo the recovered secret)",
    }
    (HERE / "LEAK_SCAN.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict, "prompt_files": prompt_files,
                      "prompt_hits": prompt_hits, "other_hits": other_hits}))


if __name__ == "__main__":
    main()
