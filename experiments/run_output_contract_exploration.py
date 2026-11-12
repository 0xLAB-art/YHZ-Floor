import hashlib
import json
import sys
import time
import uuid
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
RUNS = BASE / "sp2027/analysis/checkpoint007_active_experiments/runs_009"
OUT = Path(__file__).resolve().parent / "exploratory_output_contract_20261017"
OUT.mkdir(exist_ok=True)
(OUT / "raw_provider_responses").mkdir(exist_ok=True)
sys.path.insert(0, str(RUNS))
from fixture_qualification import rc4
from h1_campaign import ecdsa_instance
from h1_fixtures import xor_instance
from provider_adapter import ClaudeProvider, ProviderFailure


def public_instance(family, seed):
    if family == "rc4":
        key = hashlib.sha256(f"rc4-key-{seed}".encode()).digest()[:16]
        known = f"known-prefix-{seed:02d}".encode().ljust(16, b"!")[:16]
        target = hashlib.sha256(f"rc4-target-{seed}".encode()).digest()[:16]
        ks = rc4(key, bytes(64))
        public = {"known_plaintext": known.hex(), "known_ciphertext": bytes(a ^ b for a, b in zip(known, ks[:16])).hex(), "target_ciphertext": bytes(a ^ b for a, b in zip(target, ks[:16])).hex(), "known_offset": 0, "target_offset": 0}
        return public, target, "target_plaintext_hex"
    if family == "ecdsa":
        public, truth = ecdsa_instance(seed)
        return public, truth, "private_key_hex"
    public, truth, target = xor_instance(seed)
    return public, target, "mask_hex"


def prompt(family, public, field):
    return (
        "This is a prospective exploratory response-contract intervention, not part of confirmatory H1 V2. "
        "Infer the named cryptographic relation from the public observations and provide the best candidate. "
        f"Return exactly one JSON object on one line with exactly the field {field}. "
        "Do not include prose, markdown, code fences, calculations, or additional keys. "
        f"The relation family is {family}. Public observations: {json.dumps(public, sort_keys=True)}"
    )


def parse(text):
    try:
        x = json.loads(text.strip())
        return x if isinstance(x, dict) else None
    except Exception:
        return None


def main():
    protocol = "P009-H1-EXP-OUTPUT-CONTRACT-v1"
    provider = ClaudeProvider()
    rows = []
    for seed in (1, 2, 3):
        for family in ("rc4", "ecdsa", "xor"):
            public, truth, field = public_instance(family, seed)
            run_id = f"explore_20261017__{family}__seed_{seed}__{uuid.uuid4().hex[:12]}"
            text = prompt(family, public, field)
            event = {"run_id": run_id, "kind": "model_start", "time": time.time(), "family": family, "seed": seed, "protocol": protocol, "prompt_sha256": hashlib.sha256(text.encode()).hexdigest(), "provider_route": provider.model}
            with (OUT / "events.jsonl").open("a") as f:
                f.write(json.dumps(event, sort_keys=True) + "\n")
            try:
                result = provider.call(text, 256)
                raw_path = OUT / "raw_provider_responses" / f"{run_id}.json"
                raw_path.write_text(result["raw_body"])
                parsed = parse(result["text"])
                value = parsed.get(field) if parsed else None
                valid_hex = isinstance(value, str) and all(c in "0123456789abcdefABCDEF" for c in value) and len(value) > 0
                row = {"run_id": run_id, "family": family, "seed": seed, "protocol": protocol, "provider_status": "model_response", "finish_reason": result["metadata"].get("finish_reason"), "strict_json": parsed is not None, "candidate_field_present": field in parsed if parsed else False, "candidate_syntax_valid": valid_hex, "oracle_recovery": False, "oracle_note": "candidate comparison withheld from portable output; truth remains local", "input_tokens": result["metadata"].get("usage", {}).get("input_tokens", 0), "output_tokens": result["metadata"].get("usage", {}).get("output_tokens", 0), "raw_path": str(raw_path)}
                with (OUT / "events.jsonl").open("a") as f:
                    f.write(json.dumps({"run_id": run_id, "kind": "model_response", "time": time.time(), "provider_metadata": result["metadata"], "raw_response_path": str(raw_path)}, sort_keys=True) + "\n")
            except ProviderFailure as exc:
                row = {"run_id": run_id, "family": family, "seed": seed, "protocol": protocol, "provider_status": exc.category, "error": str(exc)}
                with (OUT / "events.jsonl").open("a") as f:
                    f.write(json.dumps({"run_id": run_id, "kind": "provider_failure", "time": time.time(), "category": exc.category}, sort_keys=True) + "\n")
            with (OUT / "results.jsonl").open("a") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")
            print(json.dumps({k: v for k, v in row.items() if k not in {"raw_path", "error"}}, sort_keys=True), flush=True)
            rows.append(row)
    summary = {"protocol": protocol, "calls": len(rows), "provider_responses": sum(r.get("provider_status") == "model_response" for r in rows), "strict_json": sum(r.get("strict_json", False) for r in rows), "candidate_field_present": sum(r.get("candidate_field_present", False) for r in rows), "provider_failures": sum(r.get("provider_status") != "model_response" for r in rows), "confirmatory": False, "baseline": "P009-H1-v2 same public-instance families/seeds; no model-randomness match", "interpretation": "This exploration tests only whether an explicit one-object output contract changes response formatting and candidate-field emission. It cannot establish a capability effect or causal improvement without a randomized matched design."}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
