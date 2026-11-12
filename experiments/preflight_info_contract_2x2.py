"""P010 preflight: local positive control, negative control, cell-text audit,
provider attest, and one minimal wire probe. Run BEFORE any experimental
session. Writes info_contract_2x2_20261018/preflight/*.
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parents[0] / "analysis/checkpoint007_active_experiments/runs_009"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RUNS))

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms  # noqa: E402
from run_code_feedback_chacha20 import instance, oracle, prompt as historical_prompt  # noqa: E402
from run_info_contract_2x2_chacha20 import build_prompt, CELL_SLOTS, CELLS, MIDDLE  # noqa: E402
from provider_adapter import ClaudeProvider, ProviderFailure  # noqa: E402

OUT = HERE / "info_contract_2x2_20261018" / "preflight"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = (41, 42, 43, 44)
results = {"started": time.time(), "seeds": list(SEEDS)}
fail = []

# --- 1. positive control (fixture + oracle wire) ---
pos = []
for seed in SEEDS:
    public, truth = instance(seed)
    c1 = bytes.fromhex(public["c1_hex"])
    c2 = bytes.fromhex(public["c2_hex"])
    key = hashlib.sha256(f"acts-chacha20-key-{seed}".encode()).digest()
    nonce = b"acts-nonce-2026!"
    # method A: keystream identity (reference is zero)
    p1_xor = bytes(a ^ b for a, b in zip(c1, c2))
    # method B: direct decrypt
    dec = Cipher(algorithms.ChaCha20(key, nonce), mode=None).decryptor()
    p1_dec = dec.update(c1)
    accepted = oracle({"plaintext2_hex": p1_xor.hex()}, truth)
    entry = {
        "seed": seed,
        "public_input_sha256": hashlib.sha256(json.dumps(public, sort_keys=True).encode()).hexdigest(),
        "methodA_matches_truth": p1_xor == truth,
        "methodB_matches_truth": p1_dec == truth,
        "methods_agree": p1_xor == p1_dec,
        "oracle_accepts_recovered": bool(accepted),
    }
    pos.append(entry)
    if not (entry["methodA_matches_truth"] and entry["methodB_matches_truth"] and accepted):
        fail.append(f"positive_control_failed_seed_{seed}")
(OUT / "positive_control.json").write_text(json.dumps(pos, indent=2, sort_keys=True) + "\n")
results["positive_control_all_pass"] = not fail

# --- 2. negative control ---
public41, truth41 = instance(41)
wrong = bytearray(truth41)
wrong[0] ^= 0x01
neg = {
    "wrong_candidate_rejected": not oracle({"plaintext2_hex": bytes(wrong).hex()}, truth41),
    "correct_candidate_accepted": oracle({"plaintext2_hex": truth41.hex()}, truth41),
    "non_dict_rejected": not oracle("zzz", truth41),
}
if not all(neg.values()):
    fail.append("negative_control_failed")
(OUT / "negative_control.json").write_text(json.dumps(neg, indent=2, sort_keys=True) + "\n")

# --- 3. cell-text audit ---
os.environ.pop("ACTS_PROMPT_VARIANT", None)
dummy = {"dummy": 1}
cell_audit = {"cells": {}, "c1_equals_historical_default": None, "pairwise_diff_spans": {}}
template_hashes = {}
for cell in CELLS:
    text = build_prompt(cell, dummy)
    template = text.replace(f"PUBLIC_INPUT={json.dumps(dummy, sort_keys=True)}", "PUBLIC_INPUT={PUBLIC}")
    template_hashes[cell] = hashlib.sha256(template.encode()).hexdigest()
    cell_audit["cells"][cell] = {"naming_slot": CELL_SLOTS[cell][0], "reference_slot": CELL_SLOTS[cell][1]}
hist_default = historical_prompt(dummy)
cell_audit["c1_equals_historical_default"] = (build_prompt("C1", dummy) == hist_default)
if not cell_audit["c1_equals_historical_default"]:
    fail.append("c1_not_equal_historical_default")
# pairwise structural diff: identical intro (prefix) and identical tail
# (MIDDLE + PUBLIC_INPUT); all differences absorbed by slots A and B.
prefix = "You are an authorized local cryptanalysis agent. "
tail = MIDDLE + f"PUBLIC_INPUT={json.dumps(dummy, sort_keys=True)}"
for i, a in enumerate(CELLS):
    for b in CELLS[i + 1:]:
        ta, tb = build_prompt(a, dummy), build_prompt(b, dummy)
        lo = next(k for k in range(min(len(ta), len(tb))) if ta[k] != tb[k])
        suffix_len = next(k for k in range(min(len(ta), len(tb))) if ta[len(ta) - 1 - k] != tb[len(tb) - 1 - k])
        cell_audit["pairwise_diff_spans"][f"{a}_{b}"] = {
            "common_prefix_len": lo,
            "common_suffix_len": suffix_len,
            "prefix_identical": lo >= len(prefix),
            "tail_identical": suffix_len >= len(tail),
            "diff_within_slot_region": lo >= len(prefix) and suffix_len >= len(tail),
        }
cell_audit["template_sha256"] = template_hashes
cell_audit["middle_block_sha256"] = hashlib.sha256(MIDDLE.encode()).hexdigest()
if not all(v["diff_within_slot_region"] for v in cell_audit["pairwise_diff_spans"].values()):
    fail.append("pairwise_diff_outside_slots")
(OUT / "cell_text_audit.json").write_text(json.dumps(cell_audit, indent=2, sort_keys=True) + "\n")
results["cell_text_audit_pass"] = not any(f.startswith("pairwise") or f.startswith("c1_") for f in fail)

# --- 4. provider attest + wire probe ---
provider = ClaudeProvider()
try:
    attest = provider.attest()
except ProviderFailure as exc:
    attest = {"status": exc.category, "message": exc.message}
(OUT / "provider_attest.json").write_text(json.dumps(attest, indent=2, sort_keys=True, default=str) + "\n")
results["provider_attest_status"] = attest.get("status")

wire_ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
wire = {"probe": "Reply with the single word OK.", "max_tokens": 16, "utc": wire_ts}
try:
    r = provider.call("Reply with the single word OK.", 16)
    meta = dict(r["metadata"])
    wire.update({"ok": True, "provider_metadata": meta, "text_head": r["text"][:120], "raw_body_path": None})
    raw_name = f"provider_wire_probe_raw_{wire_ts}.json"
    (OUT / raw_name).write_text(r["raw_body"])
    wire["raw_body_path"] = str(OUT / raw_name)
except ProviderFailure as exc:
    wire.update({"ok": False, "category": exc.category, "message": exc.message})
    fail.append(f"wire_probe_failed_{exc.category}")
results["wire_probe_ok"] = wire["ok"]
(OUT / f"provider_wire_probe_{wire_ts}.json").write_text(json.dumps(wire, indent=2, sort_keys=True, default=str) + "\n")

results["failures"] = fail
results["preflight_pass"] = not fail
results["finished"] = time.time()
(OUT / "preflight_summary.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
with (OUT / "preflight_runs.jsonl").open("a") as f:
    f.write(json.dumps({"utc": wire_ts, **{k: v for k, v in results.items() if k != "failures"}, "failures": fail}, sort_keys=True) + "\n")
print(json.dumps(results, indent=2, sort_keys=True))
sys.exit(0 if not fail else 1)
