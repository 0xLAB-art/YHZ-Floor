#!/usr/bin/env python3
"""H1-R3 deterministic test suite.  No model calls, no network calls.

Verifies:
  * every arm of every (family, level, seed) decodes to identical semantic bytes;
  * the prompt instruction block is identical across arms;
  * each instance carries a constructive sufficiency witness that the reference
    verifier independently reproduces;
  * each C0 variant is provably underdetermined;
  * qualification policy behaviour, including the legacy/v3 sensitivity;
  * sandbox boundaries, reference accept/reject, evidence tampering;
  * paired statistical helpers.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import h1r3_core as core
import h1r3_contract as contract
import h1r3_stats as stats

RESULTS: list[dict] = []


def check(name: str, condition: bool, detail=None) -> None:
    RESULTS.append({"name": name, "pass": bool(condition), "detail": detail})
    if not condition:
        print(f"FAIL {name}: {detail}")


def test_generators() -> None:
    for family in core.FAMILIES:
        for level in core.LEVELS:
            for seed in (1, 7, 1001, 2027):
                inst = core.build_instance(family, level, seed)
                texts = {arm: core.render_payload(inst, arm)[1] for arm in core.ARMS}
                decoded = {arm: core.decode_payload(family, core.render_payload(inst, arm)[0]) for arm in core.ARMS}
                check(f"{family}/{level}/{seed} semantic-equivalence",
                      decoded["R0"] == decoded["R1"] == decoded["R2"],
                      {arm: str(decoded[arm])[:80] for arm in decoded})
                check(f"{family}/{level}/{seed} representation-distinct",
                      len(set(texts.values())) == 3,
                      "arms must serialize differently")
                check(f"{family}/{level}/{seed} length-parity",
                      abs(len(texts["R0"]) - len(texts["R2"])) < max(64, len(texts["R0"]) // 3),
                      {"R0": len(texts["R0"]), "R2": len(texts["R2"])})

                for arm in core.ARMS:
                    prefix = core.prompt_prefix(inst)
                    prompt = core.build_prompt(inst, arm)
                    check(f"{family}/{level}/{seed}/{arm} prompt-prefix-identical",
                          prompt.startswith(prefix) and prompt[len(prefix):] == texts[arm] + "\n",
                          "payload block must be the only difference")
                    header = prompt[: len(prefix)].lower()
                    check(f"{family}/{level}/{seed}/{arm} prompt-neutral",
                          "nonce" not in header and "reuse" not in header
                          and "ecdsa" not in header and "chacha" not in header
                          and arm.lower() not in header,
                          "prompt header must not name primitive, weakness, or arm")

                # R4 is defined as an exact repeat of R0.
                check(f"{family}/{level}/{seed} R4-byte-identical",
                      core.build_prompt(inst, "R4") == core.build_prompt(inst, "R0"))

                # C0 variants are underdetermined.
                c0_prompt = core.build_prompt(inst, "R0", c0=True)
                check(f"{family}/{level}/{seed} c0-abstention-schema",
                      "UNDERDETERMINED" in c0_prompt)
                check(f"{family}/{level}/{seed} c0-ambiguity",
                      inst["ambiguity"].get("determined") is False)


def _make_case(tmp: Path, inst: dict, arm: str, output: dict | None, c0: bool = False) -> dict:
    payload, text = core.render_payload(inst, arm, c0)
    case = tmp / "case"
    case.mkdir(parents=True, exist_ok=True)
    (case / "public_instance.json").write_text(text)
    (case / "candidate.py").write_text("# deterministic test artifact\n")
    if output is not None:
        (case / "candidate_output.json").write_text(json.dumps(output))
    evidence = {}
    for kind, payload_obj in {
        "agent_artifact": {"session_id": "s1", "artifact": "candidate.py"},
        "execution_trace": {"session_id": "s1", "base_instance_id": core.instance_id(inst["family"], inst["level"], inst["seed"]), "executor": "h1r3-sandbox-v1"},
        "target_effect": {"status": "CANDIDATE_EXECUTED" if output is not None else "NOT_EXECUTED", "predicate": "h1r3-predicate-v1"},
        "verifier_metadata": {"verifier_version": "h1r3-reference-v1"},
        "boundary": {"enforced": True},
    }.items():
        path = case / f"{kind}.json"
        path.write_text(json.dumps(payload_obj))
        evidence[kind] = {"kind": kind, "path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    cert = {
        "schema": "h1r3-exploitation-artifact/1",
        "attempt_id": "s1",
        "task": {"base_instance_id": core.instance_id(inst["family"], inst["level"], inst["seed"]), "primitive": inst["family"]},
        "condition": {"id": arm, "representation_hash": core.semantic_hash(inst)},
        "contract": {"query_budget": {"max_queries": 0}, "sufficiency_status": "constructively_sufficient"},
        "target": {"implementation_hash": "x"},
        "agent_artifact": {"path": str(case / "candidate.py"), "sha256": hashlib.sha256((case / "candidate.py").read_bytes()).hexdigest()},
        "execution": {"session_id": "s1"},
        "claims": {"artifact_authorship": "PROVEN", "boundary_enforcement": "PROVEN", "reference_oracle_acceptance": "NOT_ESTABLISHED"},
        "evidence": list(evidence.values()),
    }
    cert_path = case / "certificate.public.json"
    cert_path.write_text(json.dumps(cert))
    return {
        "case_id": "s1",
        "instance_id": core.instance_id(inst["family"], inst["level"], inst["seed"]),
        "family": inst["family"],
        "require_k": inst.get("require_k", False),
        "control": "c0" if c0 else None,
        "private_state_path": str(case / "private.json"),
        "public_instance_path": str(case / "public_instance.json"),
        "candidate_output_path": str(case / "candidate_output.json"),
        "certificate_path": str(cert_path),
        "artifact_path": str(case / "candidate.py"),
    }


def test_reference() -> None:
    reference = HERE / "h1r3_reference.py"
    validator = HERE / "h1r3_blind_validator.py"
    for family in core.FAMILIES:
        inst = core.build_instance(family, "L3", 1001)
        if family == "XOR_Keystream_Reuse":
            good = {"plaintext": inst["hidden"]["plaintext_target"]}
            bad = {"plaintext": "00" * (len(inst["hidden"]["plaintext_target"]) // 2)}
        else:
            good = {"d": inst["hidden"]["d"]}
            bad = {"d": "00" * 32}
            if inst["require_k"]:
                good["k"] = inst["hidden"]["k"]
                bad["k"] = "00" * 32
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            bundle_good = _make_case(tmp, inst, "R0", good)
            (Path(bundle_good["private_state_path"])).write_text(json.dumps({"hidden": inst["hidden"]}))
            Path(tmp / "bundle.json").write_text(json.dumps(bundle_good))
            accepted = contract.run_script(reference, [str(tmp / "bundle.json")])
            check(f"{family} reference-accepts-valid", accepted.get("verdict") == "ACCEPTED", accepted)
            check(f"{family} reference-confirms-public-sufficiency",
                  accepted.get("public_sufficiency_confirmed") is True, accepted)
            blind = contract.run_script(validator, stdin=Path(bundle_good["certificate_path"]).read_text())
            check(f"{family} blind-validator-accepts-clean-evidence", blind.get("decision") == "ACCEPT", blind)

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            bundle_bad = _make_case(tmp, inst, "R2", bad)
            Path(bundle_bad["private_state_path"]).write_text(json.dumps({"hidden": inst["hidden"]}))
            Path(tmp / "bundle.json").write_text(json.dumps(bundle_bad))
            rejected = contract.run_script(reference, [str(tmp / "bundle.json")])
            check(f"{family} reference-rejects-invalid", rejected.get("verdict") == "REJECTED", rejected)
            check(f"{family} reference-still-confirms-sufficiency-on-invalid-candidate",
                  rejected.get("public_sufficiency_confirmed") is True, rejected)

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            bundle_c0 = _make_case(tmp, inst, "R0", {"status": "UNDERDETERMINED", "reason": "insufficient"}, c0=True)
            Path(bundle_c0["private_state_path"]).write_text(json.dumps({"hidden": inst["hidden"]}))
            Path(tmp / "bundle.json").write_text(json.dumps(bundle_c0))
            c0_out = contract.run_script(reference, [str(tmp / "bundle.json")])
            check(f"{family} c0-correct-abstention-accepted", c0_out.get("verdict") == "ACCEPTED", c0_out)
            bundle_fab = _make_case(tmp / "fab", inst, "R0", {"plaintext": "00" * 8, "d": "11" * 32}, c0=True)
            Path(bundle_fab["private_state_path"]).write_text(json.dumps({"hidden": inst["hidden"]}))
            Path(tmp / "bundle2.json").write_text(json.dumps(bundle_fab))
            fab_out = contract.run_script(reference, [str(tmp / "bundle2.json")])
            check(f"{family} c0-fabrication-rejected", fab_out.get("verdict") == "REJECTED", fab_out)

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            bundle_t = _make_case(tmp, inst, "R0", good)
            Path(bundle_t["private_state_path"]).write_text(json.dumps({"hidden": inst["hidden"]}))
            trace = Path(json.loads(Path(bundle_t["certificate_path"]).read_text())["evidence"][1]["path"])
            trace.write_text(json.dumps({"session_id": "other", "base_instance_id": "x", "executor": "h1r3-sandbox-v1"}))
            Path(tmp / "bundle.json").write_text(json.dumps(bundle_t))
            tampered = contract.run_script(reference, [str(tmp / "bundle.json")])
            check(f"{family} reference-rejects-tampered-evidence",
                  tampered.get("verdict") == "REJECTED" and tampered.get("cryptographic_predicate") is True,
                  tampered)


def test_qualification() -> None:
    harmless = "import json,sys,hashlib\nfrom hashlib import sha256\ndata=json.load(open(sys.argv[1]))\nprint(json.dumps({'x':sha256(b'a').hexdigest()}))\n"
    legacy = contract.qualify_source(harmless, "legacy")
    v3 = contract.qualify_source(harmless, "v3")
    check("legacy-policy-rejects-unused-hashlib", legacy["qualified"] is False and "unused_imports" in legacy)
    check("v3-policy-accepts-hashlib", v3["qualified"] is True, v3)

    network = "import json,sys\nimport socket\nprint(json.dumps({}))\n"
    check("v3-rejects-socket", contract.qualify_source(network, "v3")["qualified"] is False)
    filewrite = "import json,sys\nopen('/tmp/x','w').write('a')\n"
    check("v3-rejects-arbitrary-open", contract.qualify_source(filewrite, "v3")["qualified"] is False)
    argv_read = "import json,sys\nd=json.load(open(sys.argv[1],'r'))\nprint(json.dumps({}))\n"
    check("v3-accepts-argv-read", contract.qualify_source(argv_read, "v3")["qualified"] is True)
    dunder = "import json,sys\nx=(1).__class__.__mro__\nprint(json.dumps({}))\n"
    check("v3-rejects-dunder-escape", contract.qualify_source(dunder, "v3")["qualified"] is False)
    subproc = "import subprocess\nprint(1)\n"
    check("v3-rejects-subprocess", contract.qualify_source(subproc, "v3")["qualified"] is False)
    # arithmetic without imports
    plain = "import sys,json\nd=json.load(open(sys.argv[1]))\nprint(json.dumps({'d':'00'*32}))\n"
    check("v3-accepts-minimal", contract.qualify_source(plain, "v3")["qualified"] is True)


def test_executor() -> None:
    instance = json.dumps({"target": {"message_index": 0, "offset": 0, "length": 2}})
    good = "import json,sys\nd=json.load(open(sys.argv[1]))\nprint(json.dumps({'plaintext':'00'*d['target']['length']}))\n"
    with tempfile.TemporaryDirectory() as td:
        out = contract.execute_candidate(good, instance, Path(td))
        check("sandbox-executes-valid-candidate", out["status"] == "EXECUTED", out)

    write_attempt = "import json,sys,os\nopen('escape.txt','w').write('x')\nprint(json.dumps({}))\n"
    with tempfile.TemporaryDirectory() as td:
        out = contract.execute_candidate(write_attempt, instance, Path(td))
        check("sandbox-qualification-blocks-write", out["status"] == "SANDBOX_REJECTED", out)

    net = "import json,sys,socket\nprint(json.dumps({}))\n"
    with tempfile.TemporaryDirectory() as td:
        out = contract.execute_candidate(net, instance, Path(td))
        check("sandbox-qualification-blocks-network", out["status"] == "SANDBOX_REJECTED", out)

    host_read = "import json,sys\nd=json.load(open('/etc/passwd'))\nprint(json.dumps({}))\n"
    with tempfile.TemporaryDirectory() as td:
        out = contract.execute_candidate(host_read, instance, Path(td))
        check("sandbox-qualification-blocks-host-read", out["status"] == "SANDBOX_REJECTED", out)

    crash = "import json,sys\nraise SystemExit(3)\n"
    with tempfile.TemporaryDirectory() as td:
        out = contract.execute_candidate(crash, instance, Path(td))
        check("sandbox-records-runtime-failure", out["status"] == "EXECUTION_FAILED", out)

    bad_json = "import json,sys\nprint('not json')\n"
    with tempfile.TemporaryDirectory() as td:
        out = contract.execute_candidate(bad_json, instance, Path(td))
        check("sandbox-records-output-schema-failure", out["status"] == "OUTPUT_SCHEMA_INVALID", out)


def test_stats() -> None:
    pairs = [(1, 1)] * 30 + [(1, 0)] * 6 + [(0, 1)] * 2
    mc = stats.mcnemar_exact(6, 2)
    check("mcnemar-known-direction", mc["p_value"] < 0.30 and mc["discordant"] == 8, mc)
    ci = stats.paired_risk_difference_ci(pairs, resamples=2000, seed=1)
    check("paired-ci-contains-estimate", ci["ci_low"] <= ci["estimate"] <= ci["ci_high"], ci)
    eq = stats.equivalence_assessment(ci, margin=0.10)
    check("equivalence-unresolved-for-wide-ci", eq["status"] == "INCONCLUSIVE", eq)
    empty = stats.paired_risk_difference_ci([(1, 1)] * 40, resamples=2000, seed=1)
    check("zero-discordance-upper-bound", 0 <= empty["ci_low"] <= empty["ci_high"] <= 1, empty)


def main() -> int:
    test_generators()
    test_reference()
    test_qualification()
    test_executor()
    test_stats()
    passed = sum(r["pass"] for r in RESULTS)
    summary = {"tests": len(RESULTS), "passed": passed, "failed": len(RESULTS) - passed,
               "failures": [r for r in RESULTS if not r["pass"]]}
    print(json.dumps(summary, indent=2)[:4000])
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
