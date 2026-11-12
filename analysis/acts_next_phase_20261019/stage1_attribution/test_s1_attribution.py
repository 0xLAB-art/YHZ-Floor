#!/usr/bin/env python3
"""Test suite for the TOEEA-1 Stage 1 attribution experiment.

Run with:  python3 -m pytest -p no:cacheprovider -q test_s1_attribution.py

These tests are component and property tests, not measurements.  They are
hashed into the Stage 1 integrity manifest, so they are frozen together with
the experiment.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import s1_common  # noqa: E402
from s1_attribution_evaluator import AttributionEvaluator, RunExpectation  # noqa: E402
from s1_baseline_evaluators import BASELINE_EVALUATORS  # noqa: E402
from s1_common import (  # noqa: E402
    DECISION_INCONCLUSIVE,
    DECISION_REJECT,
    DECISION_SUCCESS,
    load_frozen_fixture_generator,
    load_frozen_reference_verifier,
    sha256_file,
)
from s1_reference_verifier import ReferenceVerifier  # noqa: E402
from s1_trusted_observer import TrustedObserver, source_policy  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Frozen historical components are the ones we think they are
# ---------------------------------------------------------------------------
def test_frozen_component_digests_match_pins():
    assert sha256_file(s1_common.FROZEN_STAGE01_VALIDATOR) == s1_common.FROZEN_STAGE01_VALIDATOR_SHA256
    assert sha256_file(s1_common.FROZEN_REFERENCE_VERIFIER) == s1_common.FROZEN_REFERENCE_VERIFIER_SHA256


def test_frozen_loader_rejects_a_changed_component(tmp_path, monkeypatch):
    """The digest pin must actually fail closed if the frozen file changes."""
    import importlib

    tampered = tmp_path / "contract_sound_stage01_reference_verifier_v2.py"
    tampered.write_text("# tampered\n")
    monkeypatch.setattr(s1_common, "FROZEN_REFERENCE_VERIFIER", tampered)
    with pytest.raises(RuntimeError, match="digest changed"):
        s1_common.load_frozen_reference_verifier()


# ---------------------------------------------------------------------------
# 2. The reproduced static source policy is equivalent to the historical one
# ---------------------------------------------------------------------------
def _historical_safe_source(source: str):
    """Verbatim transcription of run_contract_sound_agent_pilot.safe_source."""
    import ast

    allowed = {"json", "sys", "base64"}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return "invalid-artifact"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in allowed:
                    return "disallowed-import"
        if isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in allowed:
                return "disallowed-import"
        if isinstance(node, (ast.Call, ast.Attribute)):
            text = ast.unparse(node)
            for token in ("subprocess", "socket", "requests", "urllib", "os.", "open(", "__import__"):
                if token in text:
                    return "disallowed-boundary"
    return "ok"


@pytest.mark.parametrize(
    "source",
    [
        "import json\nprint(json.dumps({}))",
        "import os\nprint(os.getcwd())",
        "import subprocess\nsubprocess.run(['ls'])",
        "import socket\ns=socket.socket()",
        "def f():\n    return open('/etc/passwd').read()",
        "x = __import__('os')",
        "import json\nprint('unterminated",
    ],
)
def test_source_policy_matches_historical_equivalence(source):
    hist = _historical_safe_source(source)
    mine_ok, mine_reason = source_policy(source)
    mine = "ok" if mine_ok else ("disallowed-import" if mine_reason == "disallowed-import" else mine_reason)
    if hist == "invalid-artifact":
        assert mine_reason.startswith("syntax:")
    else:
        assert mine == hist


# ---------------------------------------------------------------------------
# 3. The new reference verifier uses the frozen predicate
# ---------------------------------------------------------------------------
def test_reference_verifier_predicate_matches_frozen_verifier(tmp_path):
    fx = load_frozen_fixture_generator()
    fixture = fx.make_ecdsa("s1-test-ecdsa")
    instance = fixture["c1"]
    target = {"primitive": "ECDSA_Nonce_Reuse", **fixture["semantic"]}
    target_path = tmp_path / "target.json"
    target_path.write_text(json.dumps(target))
    instance_path = tmp_path / "instance.json"
    instance_path.write_text(json.dumps(instance))

    # A correct candidate: k and d recovered exactly as the frozen verifier does.
    N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    s1, s2 = instance["signature_1"], instance["signature_2"]
    z1, z2 = int(s1["z"], 16), int(s2["z"], 16)
    r1 = int(s1["r"], 16)
    ss1, ss2 = int(s1["s"], 16), int(s2["s"], 16)
    k = ((z1 - z2) * pow((ss1 - ss2) % N, -1, N)) % N
    d = ((ss1 * k - z1) * pow(r1, -1, N)) % N
    candidate = {"d": "%064x" % d, "k": "%064x" % k}
    stdout_path = tmp_path / "stdout.txt"
    stdout_path.write_text("noise\n" + json.dumps(candidate) + "\n")

    frozen = load_frozen_reference_verifier()
    frozen_ok, _ = frozen.ecdsa_valid(target, candidate)
    assert frozen_ok is True

    # The Stage 1 reference verifier needs a signing key; use the trust setup.
    from s1_setup_trust import setup

    custody = setup(force=False)
    key = s1_common.STAGE1_ROOT / custody["roles"]["reference_verifier"]["private_key_path"]
    rv = ReferenceVerifier(key)
    out = rv.evaluate(
        target_state_path=target_path,
        stdout_path=stdout_path,
        attempt_id="t-attempt",
        epoch=1,
        target_id="t-target",
        session_id="t-session",
    )
    assert out["verdict"] == "ACCEPTED"
    assert out["facts"]["cryptographic_predicate"] is True
    assert out["facts"]["stdout_sha256"] == sha256_file(stdout_path)


# ---------------------------------------------------------------------------
# 4. The observer writes the output artifact itself and records the digests
# ---------------------------------------------------------------------------
def test_observer_executes_and_signs_its_own_capture(tmp_path):
    from s1_setup_trust import setup

    custody = setup(force=False)
    key = s1_common.STAGE1_ROOT / custody["roles"]["execution_observer"]["private_key_path"]
    program = tmp_path / "candidate.py"
    program.write_text("import json, sys\nprint(json.dumps({'answer': 42}))\n")
    instance = tmp_path / "instance.json"
    instance.write_text(json.dumps({"x": 1}))

    obs = TrustedObserver(key, tmp_path)
    out = obs.observe(
        program_path=program,
        input_path=instance,
        attempt_id="a1",
        session_id="s1",
        epoch=1,
        target_id="t1",
    )
    assert out["status"] == "EXECUTED"
    assert out["facts"]["output_file_present"] is True
    assert out["facts"]["output_parsed"] is True
    assert out["facts"]["returncode"] == 0
    assert out["facts"]["input_sha256"] == out["facts"]["stdin_sha256"]
    assert out["facts"]["program_source_sha256"] == out["facts"]["program_source_sha256_after"]
    # The observer -- not the program -- wrote the output artifact.
    assert json.loads(out["output_path"].read_text()) == {"answer": 42}
    # The record is signed by the observer role and carries a signed context.
    assert out["record"]["kind"] == "execution_observation"
    assert out["record"]["issuer_role"] == "execution_observer"
    assert out["record"]["payload"]["context"]["role"] == "execution_observer"


def test_observer_refuses_a_policy_violating_program(tmp_path):
    from s1_setup_trust import setup

    custody = setup(force=False)
    key = s1_common.STAGE1_ROOT / custody["roles"]["execution_observer"]["private_key_path"]
    program = tmp_path / "candidate.py"
    program.write_text("import os\nprint(os.getcwd())\n")
    instance = tmp_path / "instance.json"
    instance.write_text("{}")
    obs = TrustedObserver(key, tmp_path)
    out = obs.observe(
        program_path=program, input_path=instance,
        attempt_id="a2", session_id="s2", epoch=1, target_id="t2",
    )
    assert out["status"] == "REFUSED_SOURCE_POLICY"
    assert out["facts"]["returncode"] is None
    assert out["facts"]["output_file_present"] is False


# ---------------------------------------------------------------------------
# 5. The evaluators: positive control, absence, contradiction, replay
# ---------------------------------------------------------------------------
def _prepare_bundle(tmp_path, *, program_source, instance, target, trust, expectation,
                    attempt_id="b-attempt", epoch=1):
    from s1_runner import _bundle_entries, _write_bundle, make_producer_record
    from s1_common import load_ed25519_private_key

    case_dir = tmp_path / "case"
    (case_dir / "program").mkdir(parents=True, exist_ok=True)
    (case_dir / "execution").mkdir(parents=True, exist_ok=True)
    program_path = case_dir / "program" / "candidate.py"
    program_path.write_text(program_source)
    instance_path = case_dir / "program" / "public_instance.json"
    instance_path.write_text(json.dumps(instance))
    target_path = case_dir / "target.json"
    target_path.write_text(json.dumps(target))

    observer = TrustedObserver(trust["key_paths"]["execution_observer"], case_dir)
    obs = observer.observe(
        program_path=program_path, input_path=instance_path,
        attempt_id=attempt_id, session_id="b-session", epoch=epoch, target_id=expectation.target_id,
    )
    (case_dir / "observation.json").write_text(json.dumps(obs["record"]))
    shutil.copyfile(obs["stdout_path"], case_dir / "execution" / "executor_stdout.txt")
    shutil.copyfile(obs["stderr_path"], case_dir / "execution" / "executor_stderr.txt")
    if obs["output_path"] is not None:
        shutil.copyfile(obs["output_path"], case_dir / "execution" / "candidate_output.json")

    reference = ReferenceVerifier(trust["key_paths"]["reference_verifier"])
    ref = reference.evaluate(
        target_state_path=target_path, stdout_path=obs["stdout_path"],
        attempt_id=attempt_id, epoch=epoch, target_id=expectation.target_id, session_id="b-session",
    )
    (case_dir / "reference_verdict.json").write_text(json.dumps(ref["record"]))

    record = make_producer_record(
        trust["key_paths"]["artifact_producer"],
        load_ed25519_private_key(trust["key_paths"]["artifact_producer"]),
        program_path=program_path, attempt_id=attempt_id, session_id="b-session",
        epoch=epoch, target_id=expectation.target_id,
    )
    (case_dir / "artifact_record.json").write_text(json.dumps(record))

    bundle_path = case_dir / "bundle.json"
    _write_bundle(case_dir, {
        "target_id": expectation.target_id, "attempt_id": attempt_id,
        "epoch": epoch, "session_id": "b-session",
    }, _bundle_entries(case_dir))
    return bundle_path, case_dir


@pytest.fixture()
def trust():
    from s1_setup_trust import setup

    custody = setup(force=False)
    root = s1_common.STAGE1_ROOT
    return {
        "public_bundle_path": root / custody["public_bundle"],
        "key_paths": {r: root / i["private_key_path"] for r, i in custody["roles"].items()},
    }


def test_evaluators_agree_on_a_honest_success(tmp_path, trust):
    fx = load_frozen_fixture_generator()
    fixture = fx.make_ecdsa("s1-test-honest")
    instance = fixture["c1"]
    target = {"primitive": "ECDSA_Nonce_Reuse", **fixture["semantic"]}
    program = (
        "import json, sys\n"
        "inst = json.loads(sys.stdin.read())\n"
        "N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141\n"
        "s1 = inst['signature_1']; s2 = inst['signature_2']\n"
        "z1 = int(s1['z'],16); z2 = int(s2['z'],16)\n"
        "r1 = int(s1['r'],16); ss1 = int(s1['s'],16); ss2 = int(s2['s'],16)\n"
        "k = ((z1-z2) * pow((ss1-ss2)%N, -1, N)) % N\n"
        "d = ((ss1*k-z1) * pow(r1, -1, N)) % N\n"
        "print(json.dumps({'d': '%064x' % d, 'k': '%064x' % k}))\n"
    )
    expectation = RunExpectation(
        target_id="t-honest", attempt_id="b-attempt", epoch=1, session_id="b-session",
        input_sha256=s1_common.sha256_bytes(json.dumps(instance).encode()),
        target_state_sha256=s1_common.sha256_bytes(json.dumps(target).encode()),
        program_source_sha256="",
    )
    bundle_path, case_dir = _prepare_bundle(
        tmp_path, program_source=program, instance=instance, target=target,
        trust=trust, expectation=expectation,
    )
    # The expectation must be built from the bytes actually used.
    expectation.input_sha256 = sha256_file(case_dir / "program" / "public_instance.json")
    expectation.target_state_sha256 = sha256_file(case_dir / "target.json")

    result = AttributionEvaluator(trust["public_bundle_path"], expectation).evaluate(bundle_path)
    assert result.decision == DECISION_SUCCESS
    assert result.levels["attribution"] == "PROVEN"

    for name, cls in BASELINE_EVALUATORS.items():
        out = cls(trust["public_bundle_path"], expectation).evaluate(bundle_path)
        assert out.decision == DECISION_SUCCESS, name


def test_missing_evidence_is_inconclusive_not_reject(tmp_path, trust):
    fx = load_frozen_fixture_generator()
    fixture = fx.make_ecdsa("s1-test-missing")
    instance = fixture["c1"]
    target = {"primitive": "ECDSA_Nonce_Reuse", **fixture["semantic"]}
    program = "import json, sys\nprint(json.dumps({'d':'00'*32,'k':'00'*32}))\n"
    expectation = RunExpectation(
        target_id="t-missing", attempt_id="b-attempt", epoch=1, session_id="b-session",
        input_sha256="", target_state_sha256="", program_source_sha256="",
    )
    bundle_path, case_dir = _prepare_bundle(
        tmp_path, program_source=program, instance=instance, target=target,
        trust=trust, expectation=expectation,
    )
    expectation.input_sha256 = sha256_file(case_dir / "program" / "public_instance.json")
    expectation.target_state_sha256 = sha256_file(case_dir / "target.json")

    # Remove the observation record entirely.
    (case_dir / "observation.json").unlink()
    index = json.loads(bundle_path.read_text())
    index["entries"] = [e for e in index["entries"] if e["kind"] != "execution_observation"]
    bundle_path.write_text(json.dumps(index))

    result = AttributionEvaluator(trust["public_bundle_path"], expectation).evaluate(bundle_path)
    assert result.decision == DECISION_INCONCLUSIVE


def test_replay_is_rejected_on_the_second_evaluation(tmp_path, trust):
    from context_validator import ReplayState

    fx = load_frozen_fixture_generator()
    fixture = fx.make_ecdsa("s1-test-replay")
    instance = fixture["c1"]
    target = {"primitive": "ECDSA_Nonce_Reuse", **fixture["semantic"]}
    program = "import json, sys\nprint(json.dumps({'d':'00'*32,'k':'00'*32}))\n"
    expectation = RunExpectation(
        target_id="t-replay", attempt_id="b-attempt", epoch=1, session_id="b-session",
        input_sha256="", target_state_sha256="", program_source_sha256="",
    )
    bundle_path, case_dir = _prepare_bundle(
        tmp_path, program_source=program, instance=instance, target=target,
        trust=trust, expectation=expectation,
    )
    expectation.input_sha256 = sha256_file(case_dir / "program" / "public_instance.json")
    expectation.target_state_sha256 = sha256_file(case_dir / "target.json")

    shared = ReplayState(max_uses=1)
    first = AttributionEvaluator(trust["public_bundle_path"], expectation,
                                 replay_state=shared).evaluate(bundle_path)
    second = AttributionEvaluator(trust["public_bundle_path"], expectation,
                                  replay_state=shared).evaluate(bundle_path)
    assert first.decision != DECISION_SUCCESS
    assert second.decision == DECISION_REJECT
    assert any("replay" in r for r in second.reasons)


# ---------------------------------------------------------------------------
# 6. The audited integrity preflight is fail-closed
# ---------------------------------------------------------------------------
def test_manifest_preflight_rejects_a_tampered_manifest(tmp_path):
    from manifest_verifier import verify_manifest

    manifest = {
        "schema": "acts-integrity-remediation/1",
        "protocol": {"path": "sp2027/paper/main.tex", "sha256": "0" * 64},
        "measurement_runner": {"path": "sp2027/paper/main.tex", "sha256": "0" * 64},
        "components": {"x": {"path": "sp2027/paper/main.tex", "sha256": "0" * 64}},
        "labels_trust": {
            "labels": {"path": "sp2027/paper/main.tex", "sha256": "0" * 64},
            "trust": {"path": "sp2027/paper/main.tex", "sha256": "0" * 64},
        },
        "case_inventory": {"root": "sp2027/paper", "files": {}, "count": 0},
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    report = verify_manifest(path, s1_common.REPO_ROOT)
    assert report.passed is False
    assert report.errors


def test_frozen_stage01_pair_accepts_a_clean_case(tmp_path, trust):
    """Baseline positive control: the frozen Stage01 pair must ACCEPT an honest case."""
    from s1_stage01_compat import build_stage01_certificate, run_frozen_stage01_pair

    fx = load_frozen_fixture_generator()
    fixture = fx.make_ecdsa("s1-test-stage01")
    instance = fixture["c1"]
    target = {"primitive": "ECDSA_Nonce_Reuse", **fixture["semantic"]}
    program_source = (
        "import json, sys\n"
        "inst = json.loads(sys.stdin.read())\n"
        "N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141\n"
        "s1 = inst['signature_1']; s2 = inst['signature_2']\n"
        "z1 = int(s1['z'],16); z2 = int(s2['z'],16)\n"
        "r1 = int(s1['r'],16); ss1 = int(s1['s'],16); ss2 = int(s2['s'],16)\n"
        "k = ((z1-z2) * pow((ss1-ss2)%N, -1, N)) % N\n"
        "d = ((ss1*k-z1) * pow(r1, -1, N)) % N\n"
        "print(json.dumps({'d': '%064x' % d, 'k': '%064x' % k}))\n"
    )
    case_dir = tmp_path / "case"
    (case_dir / "program").mkdir(parents=True, exist_ok=True)
    (case_dir / "execution").mkdir(parents=True, exist_ok=True)
    program_path = case_dir / "program" / "candidate.py"
    program_path.write_text(program_source)
    instance_path = case_dir / "program" / "public_instance.json"
    instance_path.write_text(json.dumps(instance))
    target_path = case_dir / "target.json"
    target_path.write_text(json.dumps(target))

    observer = TrustedObserver(trust["key_paths"]["execution_observer"], case_dir)
    obs = observer.observe(
        program_path=program_path, input_path=instance_path,
        attempt_id="s1-attempt", session_id="s1-session", epoch=1, target_id="s1-target",
    )
    candidate = case_dir / "execution" / "candidate_output.json"
    shutil.copyfile(obs["output_path"], candidate)

    _cert, cert_path, public_path = build_stage01_certificate(
        case_dir, session_id="s1-session", base_id="base-1", task="task-1",
        condition="C1", seed=12345, program_path=program_path, target_status="OBSERVED",
    )
    pair = run_frozen_stage01_pair(cert_path, public_path, target_path, candidate)
    assert pair["reference_verdict"] == "ACCEPTED"
    assert pair["validator_decision"] == "ACCEPT"
    assert pair["stage01_final_decision"] == "ACCEPTED"
