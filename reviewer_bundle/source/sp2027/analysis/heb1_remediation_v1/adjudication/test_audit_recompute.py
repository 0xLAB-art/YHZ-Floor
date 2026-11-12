import json
from pathlib import Path

from audit_recompute import (audit_iar_a_certificates, check_target_correspondence,
                              compare_certificate_pair, recompute_common_contract)


def test_target_check_requires_matching_crypto_fields_and_hash():
    target = {"curve": "secp256k1", "public_key": ["x", "y"], "signature_1": {"r": "r"}}
    private = {"state": dict(target), "sha256": "private-hash"}
    report = check_target_correspondence(target, private, "public-hash")
    assert report["status"] == "FAIL"
    assert "crypto fields" not in report["reasons"]
    altered = {**target, "signature_1": {"r": "changed"}}
    assert check_target_correspondence(altered, private, "private-hash")["status"] == "FAIL"


def test_certificate_pair_exposes_private_claim_difference(tmp_path: Path):
    public = tmp_path / "public.json"
    private = tmp_path / "private.json"
    public.write_text(json.dumps({"claims": {"reference": "NOT_ESTABLISHED"}}))
    private.write_text(json.dumps({"claims": {"reference": "ACCEPTED"}}))
    report = compare_certificate_pair(public, private)
    assert report["status"] == "PASS"
    assert "$.claims.reference" in report["differences"]


def test_iar_a_audit_reports_all_certificate_differences(tmp_path: Path):
    (tmp_path / "A.public_certificate.json").write_text(json.dumps({"x": 1}))
    (tmp_path / "A.private_certificate.json").write_text(json.dumps({"x": 2}))
    report = audit_iar_a_certificates(tmp_path)
    assert report["integrity_status"] == "PASS"
    assert report["pairs"] == 1
    assert report["records"][0]["differences"] == ["$.x"]


def test_metrics_separate_malformed_and_substantive_denominators():
    results = {"per_case": [
        {"family": "S15", "adj": {"malformed": True, "supported": 0}, "requested": 6,
         "systems": {"v2": "REJECT"}, "asserted": {"v2": None}, "system_levels": {"v2": None}, "level6_promotion": {"v2": False}},
        {"family": "S4", "adj": {"malformed": False, "supported": 0}, "requested": 6,
         "systems": {"v2": "EMIT"}, "asserted": {"v2": 6}, "system_levels": {"v2": 6}, "level6_promotion": {"v2": False}},
        {"family": "S13", "adj": {"malformed": False, "supported": 2}, "requested": 2,
         "systems": {"v2": "REJECT"}, "asserted": {"v2": None}, "system_levels": {"v2": 2}, "level6_promotion": {"v2": False}},
    ]}
    report = recompute_common_contract(results)
    assert report["denominators"] == {"all": 3, "malformed": 1, "substantive": 2,
                                       "attack_substantive": 1, "honest_substantive": 1,
                                       "partial_claimable": 1, "honest_full_claims": 0}
    assert report["metrics"]["v2"]["false_promotion"]["denominator"] == 1
    assert report["metrics"]["v2"]["raw_rejection_coverage"]["numerator"] == 1


def test_partial_functionality_is_na_when_no_partial_cases():
    results = {"per_case": [{"family": "S4", "adj": {"malformed": False, "supported": 0},
                              "requested": 6, "systems": {"v2": "EMIT"}, "asserted": {"v2": 6}, "system_levels": {"v2": 6},
                              "level6_promotion": {"v2": True}}]}
    report = recompute_common_contract(results)
    assert report["metrics"]["v2"]["partial_acceptance"] == {
        "numerator": 0, "denominator": 0, "status": "N/A"}


def test_rejected_diagnostic_level_is_not_an_emission():
    row = {"family": "S13", "adj": {"malformed": False, "supported": 2}, "requested": 2,
           "systems": {"v3-full": "REJECT"}, "asserted": {"v3-full": None},
           "system_levels": {"v3-full": 2}, "level6_promotion": {"v3-full": True}}
    report = recompute_common_contract({"per_case": [row]})
    assert report["metrics"]["v3-full"]["partial_acceptance"]["numerator"] == 0


def test_stored_promotion_flag_does_not_drive_false_promotion():
    row = {"family": "S4", "adj": {"malformed": False, "supported": 0}, "requested": 6,
           "systems": {"v2": "REJECT"}, "asserted": {"v2": None},
           "system_levels": {"v2": 6}, "level6_promotion": {"v2": True}}
    report = recompute_common_contract({"per_case": [row]})
    assert report["metrics"]["v2"]["false_promotion"]["numerator"] == 0


def test_missing_verdict_is_inconclusive_not_zero():
    row = {"family": "S4", "adj": {"malformed": False, "supported": 0}, "requested": 6,
           "asserted": {"v2": 6}, "system_levels": {"v2": 6}}
    report = recompute_common_contract({"per_case": [row]})
    assert report["integrity_status"] == "INCONCLUSIVE"


def test_v2_partial_functionality_is_na_but_rejection_is_counted():
    row = {"family": "S13", "adj": {"malformed": False, "supported": 2}, "requested": 2,
           "systems": {"v2": "REJECT"}, "asserted": {"v2": None},
           "system_levels": {"v2": 0}, "level6_promotion": {"v2": False}}
    report = recompute_common_contract({"per_case": [row]})
    assert report["metrics"]["v2"]["partial_acceptance"]["status"] == "N/A"
    assert report["metrics"]["v2"]["raw_rejection_coverage"]["numerator"] == 1


def test_actual_accept_at_sufficient_partial_level_counts():
    row = {"family": "S13", "adj": {"malformed": False, "supported": 3}, "requested": 2,
           "systems": {"v3-full": "ACCEPT"}, "asserted": {"v3-full": 2},
           "system_levels": {"v3-full": 3}, "level6_promotion": {"v3-full": False}}
    report = recompute_common_contract({"per_case": [row]})
    assert report["metrics"]["v3-full"]["partial_acceptance"]["numerator"] == 1


def test_missing_decision_mapping_key_is_inconclusive():
    row = {"family": "S4", "adj": {"malformed": False, "supported": 0}, "requested": 6,
           "systems": {}, "asserted": {"v2": 6}, "system_levels": {"v2": 6}}
    assert recompute_common_contract({"per_case": [row]})["integrity_status"] == "INCONCLUSIVE"


def test_missing_supported_value_is_inconclusive():
    row = {"family": "S4", "adj": {"malformed": False}, "requested": 6,
           "systems": {"v2": "REJECT"}, "asserted": {"v2": None}, "system_levels": {"v2": 0}}
    assert recompute_common_contract({"per_case": [row]})["integrity_status"] == "INCONCLUSIVE"


def test_stronger_accepted_claim_counts_requested_promotion():
    row = {"family": "S4", "adj": {"malformed": False, "supported": 4}, "requested": 5,
           "systems": {"v3-full": "ACCEPT"}, "asserted": {"v3-full": 6},
           "system_levels": {"v3-full": 6}}
    report = recompute_common_contract({"per_case": [row]})
    assert report["metrics"]["v3-full"]["false_promotion"]["numerator"] == 1
    assert report["metrics"]["v3-full"]["level6_false_promotion"]["numerator"] == 1


def test_system_cohort_mismatch_is_inconclusive():
    base = {"family": "S4", "adj": {"malformed": False, "supported": 0}, "requested": 6,
            "asserted": {"v2": None}, "system_levels": {"v2": 0}}
    first = {**base, "systems": {"v2": "REJECT"}}
    second = {**base, "systems": {"v3-full": "REJECT"}, "asserted": {"v3-full": None},
              "system_levels": {"v3-full": 0}}
    assert recompute_common_contract({"per_case": [first, second]})["integrity_status"] == "INCONCLUSIVE"
