"""P011 preflight: local deterministic gates, run BEFORE any experimental
session and AFTER the preregistration freeze commit (no model calls here;
provider health was verified by the separate AUTH_SMOKE probe).

Hard gates (any failure => phase NO-GO, no sessions launched):
  1. Positive control: for each seed 81-84 the local solver recovers the
     target plaintext VIA THE REFERENCE (B+ premise: reference is the fixed
     32-byte all-zero constant) and the P009-pattern oracle accepts; a second
     independent method (direct RC4 keystream from the seed key derivation)
     agrees. Wrong candidate rejected (negative control).
  2. Underdetermination witness: with the reference value withheld, the
     public JSON does not determine the exact-match answer -- at least two
     distinct reference contents yield distinct candidate plaintexts, each
     fully consistent with every public field. Witness retained.
  3. Cell-text audit: all four cell templates share an identical intro prefix
     and identical tail (MIDDLE + PUBLIC_INPUT block); every pairwise
     difference is confined to the A/B slot region. Also records the
     continuity assertion that the A+ opening sentence matches the historical
     named RC4 prompt's naming sentence verbatim (non-gating).

Writes preflight/{positive_control,negative_control,ambiguity_witness,
cell_text_audit,provider_attest,preflight_summary}.json and
preflight/preflight_runs.jsonl. Exit 1 on any hard-gate failure.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rc4_fixture import (  # noqa: E402
    A_PLUS, CELLS, CELL_SLOTS, CLAIM_FIELD, MIDDLE, PROMPT_PREFIX, PROTOCOL,
    REFERENCE, SEEDS, build_prompt, candidate_for_reference, instance, oracle,
    rc4_encrypt, solve_via_reference,
)
from provider_client import ClaudeProvider  # noqa: E402

OUT = HERE / "preflight"
OUT.mkdir(parents=True, exist_ok=True)

# Historical named RC4 prompt opening (run_code_feedback_rc4.py, default
# variant) -- used ONLY as a continuity assertion; the historical run used a
# different fixture (known-plaintext) and is never pooled.
HISTORICAL_RC4_NAMED_OPENING = "This is a qualified synthetic RC4 keystream-reuse instance. "

ALT_REFERENCES = (b"A" * 32, bytes(range(32)))  # witnesses for withheld-premise world


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    started = time.time()
    results = {"protocol": PROTOCOL, "started": started, "seeds": list(SEEDS)}
    failures = []

    # --- 1. positive control (solver via reference + independent direct RC4) ---
    pos = []
    for seed in SEEDS:
        public, truth = instance(seed)
        via_ref = solve_via_reference(public)
        key = hashlib.sha256(f"acts-rc4-key-{seed}".encode()).digest()[:16]
        from rc4_fixture import NONCE
        keystream = rc4_encrypt(key, NONCE, b"\x00" * len(truth))  # direct keystream, no reference route
        direct = bytes(a ^ b for a, b in zip(bytes.fromhex(public["c_target_hex"]), keystream))
        entry = {
            "seed": seed,
            "public_input_sha256": hashlib.sha256(json.dumps(public, sort_keys=True).encode()).hexdigest(),
            "methodA_via_reference_matches_truth": via_ref == truth,
            "methodB_direct_rc4_matches_truth": direct == truth,
            "methods_agree": via_ref == direct,
            f"oracle_accepts_recovered_{CLAIM_FIELD}": bool(oracle({CLAIM_FIELD: via_ref.hex()}, truth)),
        }
        pos.append(entry)
        if not all(v for k, v in entry.items() if k not in ("seed", "public_input_sha256")):
            failures.append(f"positive_control_failed_seed_{seed}")
    (OUT / "positive_control.json").write_text(json.dumps(pos, indent=2, sort_keys=True) + "\n")
    results["positive_control_all_pass"] = not any(f.startswith("positive_control") for f in failures)

    # --- 2. negative control ---
    public81, truth81 = instance(81)
    wrong = bytearray(truth81)
    wrong[0] ^= 0x01
    neg = {
        "wrong_candidate_rejected": not oracle({CLAIM_FIELD: bytes(wrong).hex()}, truth81),
        "correct_candidate_accepted": oracle({CLAIM_FIELD: truth81.hex()}, truth81),
        "non_dict_rejected": not oracle("zzz", truth81),
    }
    if not all(neg.values()):
        failures.append("negative_control_failed")
    (OUT / "negative_control.json").write_text(json.dumps(neg, indent=2, sort_keys=True) + "\n")

    # --- 3. underdetermination witness (withheld reference value) ---
    witness = {
        "claim": ("With the reference content withheld, the public JSON does not determine a unique "
                  "exact-match answer: for any 32-byte reference R, candidate = c_target XOR c_ref XOR R "
                  "is consistent with every public field; only the true R yields the oracle-accepted hex."),
        "seeds": {},
    }
    for seed in SEEDS:
        public, truth = instance(seed)
        base = solve_via_reference(public)  # candidate under R = all-zero reference
        alts = {r.hex(): candidate_for_reference(public, r) for r in ALT_REFERENCES}
        consistent = {
            "all_zero_reference": {
                "reference_hex": REFERENCE.hex(),
                "candidate_hex": base.hex(),
                "is_truth": base == truth,
            },
        }
        for rhex, cand in alts.items():
            consistent[rhex] = {
                "reference_hex": rhex,
                "candidate_hex": cand.hex(),
                "is_truth": cand == truth,
            }
        # every candidate is consistent with the public fields by construction:
        # reconstructing c_target = candidate XOR c_ref XOR R reproduces the public ciphertext
        recon_ok = True
        for rbytes, cand in [(REFERENCE, base)] + list(zip(ALT_REFERENCES, alts.values())):
            recon = bytes(a ^ b for a, b in zip(
                bytes(a ^ b for a, b in zip(cand, bytes.fromhex(public["c_ref_hex"]))), rbytes))
            recon_ok = recon_ok and (recon == bytes.fromhex(public["c_target_hex"]))
        distinct_candidates = len({c.hex() for c in [base, *alts.values()]})
        entry = {
            "public_input": public,
            "candidates_by_assumed_reference": consistent,
            "all_candidates_consistent_with_public_fields": recon_ok,
            "distinct_candidate_count": distinct_candidates,
            "underdetermined_for_exact_match": distinct_candidates >= 2 and recon_ok,
            "note": ("The RC4 effective key is not derivable from the public JSON (no keystream is "
                     "exposed without the reference premise), so no public route pins R."),
        }
        witness["seeds"][str(seed)] = entry
        if not (entry["underdetermined_for_exact_match"] and recon_ok):
            failures.append(f"underdetermination_witness_failed_seed_{seed}")
    (OUT / "ambiguity_witness.json").write_text(json.dumps(witness, indent=2, sort_keys=True) + "\n")
    results["ambiguity_witness_pass"] = not any(f.startswith("underdetermination") for f in failures)

    # --- 4. cell-text audit ---
    dummy = {"dummy": 1}
    audit = {"cells": {}, "pairwise_diff_spans": {}, "template_sha256": {}}
    for cell in CELLS:
        text = build_prompt(cell, dummy)
        template = text.replace(f"PUBLIC_INPUT={json.dumps(dummy, sort_keys=True)}", "PUBLIC_INPUT={PUBLIC}")
        audit["template_sha256"][cell] = sha(template.encode())
        audit["cells"][cell] = {"naming_slot": CELL_SLOTS[cell][0], "reference_slot": CELL_SLOTS[cell][1]}
    audit["a_plus_matches_historical_named_rc4_opening"] = (A_PLUS == HISTORICAL_RC4_NAMED_OPENING)
    audit["historical_continuity_note"] = ("Continuity assertion only: the historical RC4 run used a "
                                           "different known-plaintext fixture and different full prompt; "
                                           "byte-equality with it is neither expected nor required.")
    prefix = PROMPT_PREFIX
    tail = MIDDLE + f"PUBLIC_INPUT={json.dumps(dummy, sort_keys=True)}"
    for i, a in enumerate(CELLS):
        for b in CELLS[i + 1:]:
            ta, tb = build_prompt(a, dummy), build_prompt(b, dummy)
            lo = next(k for k in range(min(len(ta), len(tb))) if ta[k] != tb[k])
            suffix_len = next(k for k in range(min(len(ta), len(tb)))
                              if ta[len(ta) - 1 - k] != tb[len(tb) - 1 - k])
            audit["pairwise_diff_spans"][f"{a}_{b}"] = {
                "common_prefix_len": lo,
                "common_suffix_len": suffix_len,
                "prefix_identical": lo >= len(prefix),
                "tail_identical": suffix_len >= len(tail),
                "diff_within_slot_region": lo >= len(prefix) and suffix_len >= len(tail),
            }
    audit["middle_block_sha256"] = sha(MIDDLE.encode())
    if not all(v["diff_within_slot_region"] for v in audit["pairwise_diff_spans"].values()):
        failures.append("pairwise_diff_outside_slots")
    (OUT / "cell_text_audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    results["cell_text_audit_pass"] = not any(f.startswith("pairwise") for f in failures)

    # --- 5. provider attest (metadata only; non-evidence) ---
    provider = ClaudeProvider()
    try:
        attest = provider.attest()
    except Exception as exc:  # noqa: BLE001
        attest = {"status": "PROVIDER_UNAVAILABLE", "error_category": type(exc).__name__}
    (OUT / "provider_attest.json").write_text(json.dumps(attest, indent=2, sort_keys=True, default=str) + "\n")
    results["provider_attest_status"] = attest.get("status")

    results["failures"] = failures
    results["preflight_pass"] = not failures
    results["finished"] = time.time()
    (OUT / "preflight_summary.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    with (OUT / "preflight_runs.jsonl").open("a") as f:
        f.write(json.dumps({"utc": time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()),
                            **results}, sort_keys=True) + "\n")
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
