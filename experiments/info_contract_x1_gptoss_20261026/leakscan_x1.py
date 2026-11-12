#!/usr/bin/env python3
"""P010X1 leak scan.

For every seed 161-176, compute the fixture truth (ChaCha20 plaintext hex and
key hex) with the SAME derivation as run_code_feedback_chacha20.instance,
then scan every text-readable file under this namespace (except
execution_captures, by design — accepted-program stdout may echo the
recovered plaintext — and except the scanner's own outputs) for those
secrets in raw/lower/upper/spaced forms. Prompts must contain none. Writes
LEAK_SCAN.json.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from run_code_feedback_chacha20 import instance  # noqa: E402

HERE = Path(__file__).resolve().parent
SEEDS = list(range(161, 177))


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

    prompt_hits, prompt_hit_detail, prompt_files = 0, [], 0
    for p in sorted((HERE / "prompts").glob("*.txt")):
        prompt_files += 1
        text = p.read_text(errors="replace")
        for seed, s in secrets.items():
            hit_any = False
            for field in ("truth_hex", "key_hex"):
                for form in variants(s[field]):
                    if form and form in text:
                        prompt_hits += 1
                        prompt_hit_detail.append({"file": p.name, "seed": seed, "form": field})
                        hit_any = True
                        break
                if hit_any:
                    break

    other_hits, other_hit_detail = 0, []
    skip = {"LEAK_SCAN.json", "all_artifacts.sha256"}
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
            hit_any = False
            for field in ("truth_hex", "key_hex"):
                for form in variants(s[field]):
                    if form and form in text:
                        other_hits += 1
                        other_hit_detail.append({"file": str(p.relative_to(HERE)), "seed": seed, "form": field})
                        hit_any = True
                        break
                if hit_any:
                    break

    verdict = "PASS" if prompt_hits == 0 else "FAIL"
    out = {
        "schema": "infoc-x1-leakscan/1",
        "protocol": "P010X1-INFO-CONTRACT-2X2-CHACHA20-GPTOSS120B-v1",
        "seeds": SEEDS,
        "prompt_files": prompt_files,
        "prompt_hits": prompt_hits,
        "prompt_hit_detail": prompt_hit_detail,
        "other_json_hits": other_hits,
        "other_json_hit_detail": other_hit_detail,
        "verdict": verdict,
        "note": "execution_captures excluded by design (accepted-program stdout may echo the recovered plaintext)",
    }
    (HERE / "LEAK_SCAN.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict, "prompt_files": prompt_files,
                      "prompt_hits": prompt_hits, "other_hits": other_hits}))


if __name__ == "__main__":
    main()
