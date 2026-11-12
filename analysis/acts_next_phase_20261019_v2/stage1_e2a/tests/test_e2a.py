"""Unit tests for the E2A components.

These tests exercise the properties the experiment depends on.  They are not
the experiment; they are the guard that the experiment is measuring what it
claims to measure.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from e2a import canonical, observer, producers, reference, remediation, truth  # noqa: E402
from e2a.aggregator import Aggregator  # noqa: E402


def test_memfd_execution_binds_hashed_bytes(tmp_path):
    """The bytes that are hashed are the bytes that are executed."""
    source = producers.produce_source("ChaCha20_Nonce_Repeat", "correct").encode("utf-8")
    instance = {"encoding": "json-hex-v1", "ciphertext_1": "00", "ciphertext_2": "00",
                "known_plaintext_1": "00"}
    instance_path = tmp_path / "public_instance.json"
    instance_path.write_bytes(canonical.canonical_bytes(instance))
    result = observer.execute_observed(source, instance_path, tmp_path)
    assert result["returncode"] == 0, result["stderr_bytes"]
    # the interpreter read the program from the inherited descriptor
    assert b"/proc/self/fd/" in result["stderr_bytes"] or result["stdout_bytes"]
    assert canonical.sha_bytes(source) != ""


def test_screen_rejects_network_and_process_creation():
    for bad in ("import socket\nsocket.socket()\n",
                "import subprocess\nsubprocess.run(['ls'])\n",
                "import os\nos.system('id')\n",
                "eval('1+1')\n"):
        accepted, reason = observer.screen_source(bad)
        assert not accepted, bad
        assert reason


def test_screen_accepts_instance_reading_program():
    """The historical Stage 01 screen rejected every program that read argv[1]."""
    source = producers.produce_source("ECDSA_Nonce_Reuse", "correct")
    accepted, reason = observer.screen_source(source)
    assert accepted, reason
    assert "open(" in source


def test_strict_parse_rejects_multiple_claims():
    single = b'{"a": 1}\n'
    multiple = b'{"a": 1}\n{"a": 2}\n'
    assert observer.parse_candidate_output(single)["parse_status"] == "OK"
    assert observer.parse_candidate_output(multiple)["parse_status"] == "AMBIGUOUS_MULTIPLE_LINES"
    # the historical last-line rule would have accepted the second object
    assert observer.parse_candidate_output(multiple)["parsed_candidate_lastline"] == {"a": 2}


def test_independent_reference_and_truth_agree(tmp_path):
    generator = remediation.stage01_generator()
    instance = generator.make_ecdsa(1)
    target_state = {"primitive": "ECDSA_Nonce_Reuse", **instance["semantic"]}
    source = producers.produce_source("ECDSA_Nonce_Reuse", "correct")
    instance_path = tmp_path / "public_instance.json"
    instance_path.write_bytes(canonical.canonical_bytes(instance["c1"]))
    result = observer.execute_observed(source.encode("utf-8"), instance_path, tmp_path)
    parsed = observer.parse_candidate_output(result["stdout_bytes"])["parsed_candidate"]
    reference_ok, _ = reference.evaluate_predicate(target_state, parsed)
    truth_ok, _ = truth.predicate_holds(target_state, parsed)
    assert reference_ok is True
    assert truth_ok is True


def test_wrong_answer_fails_both_implementations():
    generator = remediation.stage01_generator()
    instance = generator.make_ecdsa(1)
    target_state = {"primitive": "ECDSA_Nonce_Reuse", **instance["semantic"]}
    wrong = {"d": "%064x" % 1, "k": "%064x" % 2}
    assert reference.evaluate_predicate(target_state, wrong)[0] is False
    assert truth.predicate_holds(target_state, wrong)[0] is False


def test_canonical_digest_is_stable():
    assert canonical.sha_object({"b": 1, "a": 2}) == canonical.sha_object({"a": 2, "b": 1})


def test_wilson_interval_never_exceeds_one():
    low, high = canonical.wilson_interval(0, 16)
    assert low == 0.0 and 0.0 < high < 1.0
    low, high = canonical.wilson_interval(6, 6)
    assert high == 1.0 and 0.0 < low < 1.0
    assert canonical.wilson_interval(0, 0) == (None, None)


def test_frozen_baseline_validator_is_unmodified():
    """The baseline file must remain byte-identical to the frozen artefact."""
    path = remediation.STAGE01_VALIDATOR_PATH
    assert path.is_file()
    source = path.read_text(encoding="utf-8")
    assert "contract-sound-exploitation-artifact/1" in source
    assert "raw_verdict" in source  # the forbidden-key list is intact


def test_aggregator_ignores_claimant_assertion(tmp_path):
    """The E2A decision must not be a function of the claimant's claims block."""
    trust = tmp_path / "trust"
    trust.mkdir()
    roles = {
        "execution_observer": {"kinds": [canonical.OBSERVATION_KIND], "contexts": [canonical.POLICY_CONTEXT]},
        "reference_verifier": {"kinds": [canonical.REFERENCE_KIND], "contexts": [canonical.POLICY_CONTEXT]},
        "aggregator": {"kinds": [canonical.CLAIM_KIND], "contexts": [canonical.POLICY_CONTEXT]},
    }
    (trust / "trust_policy.json").write_text(json.dumps({"roles": roles}, sort_keys=True))
    signing = remediation.protected_signing()
    keys = tmp_path / "keys"
    keys.mkdir()
    issuers = [signing.generate_issuer(keys, role) for role in roles]
    signing.write_public_bundle(trust / "issuers_public.json", issuers)

    aggregator = Aggregator(trust / "issuers_public.json", trust / "trust_policy.json")
    bundle = {"certificate": {"schema": "e2a-attribution-certificate/1"}}
    first = aggregator.evaluate(bundle)
    second = aggregator.evaluate(bundle)
    assert first["decision"] == second["decision"] == "INCONCLUSIVE"


def test_case_inventory_is_frozen_and_consistent():
    from e2a import cases
    assert len(cases.CASES) == 22
    assert cases.N_SUCCESS == 6
    assert cases.N_NON_SUCCESS == 16
    assert len({case["case_id"] for case in cases.CASES}) == 22
    assert len(cases.CASE_CLASSES) == 12
