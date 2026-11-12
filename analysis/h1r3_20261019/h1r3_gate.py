#!/usr/bin/env python3
"""H1-R3 deterministic pre-provider gate.

For every (family, level, seed, arm) it:
  * renders the prompt and verifies arm invariants;
  * runs a mechanical solver program through the real OS sandbox;
  * adjudicates it with the independent reference verifier;
  * runs a wrong-answer program and confirms rejection;
  * runs the C0 abstention control;
  * records the legacy-policy sensitivity of the observed solver programs.

No provider or network calls are made.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import h1r3_contract as contract
import h1r3_core as core
import h1r3_witness_program as witness
from h1r3_run import build_certificate, sha_file, sha_text, write_json

SEEDS = [5001, 5002, 6001, 6002, 6003]


def adjudicate(case_dir: Path, session: dict, execution: dict, executed: bool, is_c0: bool) -> dict:
    cert = build_certificate(case_dir, session, execution, executed)
    cert_path = case_dir / "certificate.private.json"
    write_json(cert_path, cert)
    bundle = {
        "case_id": session["session_id"], "instance_id": session["instance_id"],
        "family": session["family"], "require_k": session.get("require_k", False),
        "control": "c0" if is_c0 else None,
        "private_state_path": str(case_dir / "private_state.json"),
        "public_instance_path": str(case_dir / "public_instance.json"),
        "candidate_output_path": str(case_dir / "candidate_output.json"),
        "certificate_path": str(cert_path), "artifact_path": str(case_dir / "candidate.py"),
    }
    write_json(case_dir / "reference_bundle.json", bundle)
    return contract.run_script(HERE / "h1r3_reference.py", [str(case_dir / "reference_bundle.json")])


def main() -> int:
    failures = []
    rows = []
    for family in core.FAMILIES:
        for level in core.LEVELS:
            for seed in SEEDS:
                inst = core.build_instance(family, level, seed)
                for arm in core.ARMS:
                    instance_id = core.instance_id(family, level, seed)
                    session = {"session_id": f"gate-{instance_id}-{arm}", "instance_id": instance_id,
                               "family": family, "level": level, "seed": seed, "arm": arm,
                               "require_k": inst.get("require_k", False),
                               "payload_sha256": core.semantic_hash(inst)}
                    with tempfile.TemporaryDirectory() as td:
                        case = Path(td)
                        payload, text = core.render_payload(inst, arm)
                        (case / "public_instance.json").write_text(text)
                        write_json(case / "private_state.json",
                                   {"family": family, "level": level, "seed": seed,
                                    "hidden": inst["hidden"], "witness": inst["witness"],
                                    "ambiguity": inst["ambiguity"]})
                        source = witness.solution_source(family, inst.get("require_k", False))
                        exec_out = contract.execute_candidate(source, text, case, policy="v3")
                        executed = exec_out["status"] == "EXECUTED"
                        if executed:
                            write_json(case / "candidate_output.json", exec_out["output"])
                        ref = adjudicate(case, session, exec_out, executed, is_c0=False)
                        ok = exec_out["status"] == "EXECUTED" and ref.get("verdict") == "ACCEPTED"
                        rows.append({"family": family, "level": level, "seed": seed, "arm": arm,
                                     "solver_execution": exec_out["status"],
                                     "solver_verdict": ref.get("verdict"),
                                     "public_sufficiency_confirmed": ref.get("public_sufficiency_confirmed"),
                                     "ok": ok})
                        if not ok:
                            failures.append({"case": f"{instance_id}/{arm}", "stage": "solver",
                                             "execution": exec_out, "reference": ref})

                        wrong = witness.WRONG_XOR if family == "XOR_Keystream_Reuse" else witness.WRONG_ECDSA
                        wrong_case = case / "wrong"
                        wrong_case.mkdir()
                        (wrong_case / "public_instance.json").write_text(text)
                        write_json(wrong_case / "private_state.json",
                                   {"hidden": inst["hidden"]})
                        w_exec = contract.execute_candidate(wrong, text, wrong_case, policy="v3")
                        if w_exec["status"] == "EXECUTED":
                            write_json(wrong_case / "candidate_output.json", w_exec["output"])
                        w_ref = adjudicate(wrong_case, session, w_exec, w_exec["status"] == "EXECUTED", is_c0=False)
                        if w_ref.get("verdict") != "REJECTED":
                            failures.append({"case": f"{instance_id}/{arm}", "stage": "wrong-answer",
                                             "reference": w_ref})
                        rows[-1]["wrong_answer_rejected"] = w_ref.get("verdict") == "REJECTED"

                        # Legitimate solver must not be rejected by the v3 policy
                        # but would have been rejected by the legacy policy if it
                        # imports a computationally inert module.
                        rows[-1]["solver_imports"] = contract.qualify_source(source, "v3")["imported_modules"]

                # C0 abstention control, one arm per instance.
                session = {"session_id": f"gate-{instance_id}-c0", "instance_id": instance_id,
                           "family": family, "level": level, "seed": seed, "arm": "R0",
                           "require_k": inst.get("require_k", False),
                           "payload_sha256": core.semantic_hash(inst, c0=True)}
                with tempfile.TemporaryDirectory() as td:
                    case = Path(td)
                    _, text = core.render_payload(inst, "R0", c0=True)
                    (case / "public_instance.json").write_text(text)
                    write_json(case / "private_state.json", {"hidden": inst["hidden"]})
                    exec_out = contract.execute_candidate(witness.ABSTAIN, text, case, policy="v3")
                    if exec_out["status"] == "EXECUTED":
                        write_json(case / "candidate_output.json", exec_out["output"])
                    ref = adjudicate(case, session, exec_out, exec_out["status"] == "EXECUTED", is_c0=True)
                    c0_ok = ref.get("verdict") == "ACCEPTED"
                    rows.append({"family": family, "level": level, "seed": seed, "arm": "C0",
                                 "solver_execution": exec_out["status"],
                                 "solver_verdict": ref.get("verdict"), "ok": c0_ok})
                    if not c0_ok:
                        failures.append({"case": f"{instance_id}/c0", "stage": "abstention", "reference": ref})

                    # Fabricating a unique answer on an underdetermined
                    # observation must be rejected.
                    fab = witness.WRONG_XOR if family == "XOR_Keystream_Reuse" else witness.WRONG_ECDSA
                    fab_case = case / "fabricate"
                    fab_case.mkdir()
                    (fab_case / "public_instance.json").write_text(text)
                    write_json(fab_case / "private_state.json", {"hidden": inst["hidden"]})
                    f_exec = contract.execute_candidate(fab, text, fab_case, policy="v3")
                    if f_exec["status"] == "EXECUTED":
                        write_json(fab_case / "candidate_output.json", f_exec["output"])
                    f_ref = adjudicate(fab_case, session, f_exec, f_exec["status"] == "EXECUTED", is_c0=True)
                    if f_ref.get("verdict") != "REJECTED":
                        failures.append({"case": f"{instance_id}/c0-fabricate", "stage": "fabrication",
                                         "reference": f_ref})

    # Arm invariant summary
    invariants = []
    for family in core.FAMILIES:
        for level in core.LEVELS:
            for seed in SEEDS:
                inst = core.build_instance(family, level, seed)
                texts = {arm: core.render_payload(inst, arm)[1] for arm in core.ARMS}
                decoded = {arm: core.decode_payload(family, core.render_payload(inst, arm)[0]) for arm in core.ARMS}
                prefixes = {arm: core.prompt_prefix(inst) for arm in core.ARMS}
                invariants.append({
                    "instance_id": core.instance_id(family, level, seed),
                    "semantic_equality": decoded["R0"] == decoded["R1"] == decoded["R2"],
                    "representation_distinct": len(set(texts.values())) == 3,
                    "prompt_prefix_identical": len(set(prefixes.values())) == 1,
                    "R4_equals_R0": core.build_prompt(inst, "R4") == core.build_prompt(inst, "R0"),
                    "payload_chars": {arm: len(texts[arm]) for arm in core.ARMS},
                })

    summary = {
        "gate": "H1R3_DETERMINISTIC_GATE",
        "solver_cases": sum(1 for r in rows if r.get("arm") in core.ARMS),
        "solver_failures": sum(1 for r in rows if r.get("arm") in core.ARMS and not r["ok"]),
        "wrong_answer_rejections": sum(1 for r in rows if r.get("wrong_answer_rejected")),
        "c0_cases": sum(1 for r in rows if r["arm"] == "C0"),
        "c0_failures": sum(1 for r in rows if r["arm"] == "C0" and not r["ok"]),
        "invariant_instances": len(invariants),
        "invariants_all_hold": all(i["semantic_equality"] and i["representation_distinct"]
                                   and i["prompt_prefix_identical"] and i["R4_equals_R0"]
                                   for i in invariants),
        "failures": failures[:20],
        "passed": not failures and all(i["semantic_equality"] and i["representation_distinct"]
                                       and i["prompt_prefix_identical"] and i["R4_equals_R0"]
                                       for i in invariants),
    }
    print(json.dumps(summary, indent=2)[:6000])
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
        write_json(out, {"summary": summary, "rows": rows, "invariants": invariants})
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
