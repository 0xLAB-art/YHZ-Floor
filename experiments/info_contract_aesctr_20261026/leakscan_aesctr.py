#!/usr/bin/env python3
"""P013 AES-CTR leak scan.

For every seed 181-196, compute the fixture truth (the 64-byte secret
protected by c1) with the SAME derivation as run_info_contract_2x2_aesctr.
instance, then scan every text-readable file under this namespace (except
execution_captures, by design — accepted-program stdout may echo the
recovered secret — and except the scanner's own outputs) for those secrets
in raw/lower/upper/spaced forms. Prompts must contain none.

Additionally, the premise content ("START_OF_RECORD") is the ONLY
fixture-truth string allowed in prompts, and only in the premise-stated
arms: it must appear in zero C2/C4 prompts (the withheld-premise arms),
while its appearance in C1/C3 prompts is by design.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from run_info_contract_2x2_aesctr import instance  # noqa: E402

HERE = Path(__file__).resolve().parent
SEEDS = list(range(181, 197))
PREMISE_TOKEN = "START_OF_RECORD"


def variants(hexstr: str):
    spaced = " ".join(hexstr[i:i + 2] for i in range(0, len(hexstr), 2))
    return {hexstr, hexstr.upper(), spaced, spaced.upper()}


def main():
    secrets = {}
    for seed in SEEDS:
        public, truth = instance(seed)
        secrets[seed] = {
            "truth_hex": truth.hex(),
            "public_input_sha256": hashlib.sha256(json.dumps(public, sort_keys=True).encode()).hexdigest(),
        }

    prompt_files, secret_hits, secret_hit_detail = 0, 0, []
    premise_in_withheld, premise_withheld_detail = 0, []
    premise_in_stated = 0
    for p in sorted((HERE / "prompts").glob("*.txt")):
        prompt_files += 1
        text = p.read_text(errors="replace")
        for seed, s in secrets.items():
            for form in variants(s["truth_hex"]):
                if form and form in text:
                    secret_hits += 1
                    secret_hit_detail.append({"file": p.name, "seed": seed, "form": "truth"})
                    break
        arm = "C1" if "__C1__" in p.name else "C3" if "__C3__" in p.name else \
              "C2" if "__C2__" in p.name else "C4" if "__C4__" in p.name else "unknown"
        if PREMISE_TOKEN in text:
            if arm in ("C1", "C3"):
                premise_in_stated += 1
            elif arm in ("C2", "C4"):
                premise_in_withheld += 1
                premise_withheld_detail.append({"file": p.name, "arm": arm})

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
            for form in variants(s["truth_hex"]):
                if form and form in text:
                    other_hits += 1
                    other_hit_detail.append({"file": str(p.relative_to(HERE)), "seed": seed})
                    break

    verdict = "PASS" if secret_hits == 0 and premise_in_withheld == 0 else "FAIL"
    out = {
        "schema": "infoc-aesctr-leakscan/1",
        "protocol": "P013-INFO-CONTRACT-2X2-AESCTR-KEYSTREAM-REUSE-v1",
        "seeds": SEEDS,
        "prompt_files": prompt_files,
        "secret_in_prompt_hits": secret_hits,
        "secret_in_prompt_hit_detail": secret_hit_detail,
        "premise_token_in_stated_arms": premise_in_stated,
        "premise_token_in_withheld_arms": premise_in_withheld,
        "premise_token_in_withheld_detail": premise_withheld_detail,
        "other_json_hits": other_hits,
        "other_json_hit_detail": other_hit_detail,
        "verdict": verdict,
        "note": ("execution_captures excluded by design (accepted-program stdout may echo the "
                 "recovered secret); premise token in C1/C3 prompts is the preregistered design"),
    }
    (HERE / "LEAK_SCAN.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict, "prompt_files": prompt_files,
                      "secret_hits": secret_hits, "premise_in_withheld": premise_in_withheld,
                      "premise_in_stated": premise_in_stated, "other_hits": other_hits}))


if __name__ == "__main__":
    main()
