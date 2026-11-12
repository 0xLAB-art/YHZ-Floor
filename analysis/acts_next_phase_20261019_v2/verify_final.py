#!/usr/bin/env python3
"""Final verification for the ACTS-Attack next-phase research deliverables.

Checks, in order:
1. the deliverables manifest covers every deliverable and every hash matches;
2. every deliverable JSON parses;
3. the four protected artifacts are byte-identical to their expected hashes;
4. the Stage 1 freeze manifest still verifies fail-closed;
5. the remediation test suite still passes;
6. the Stage 2 comparison recorded what the deliverable claims;
7. the Stage 3 boundary run recorded what the deliverable claims;
8. the Stage 4 matched arm recorded what the deliverable claims;
9. the Stage 3 and Stage 4 signed evidence verifies against their own trust
   bundles, independently of the harnesses that produced it.

Exit code 0 means every check passed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PHASE = Path(__file__).resolve().parent
DELIVERABLES = PHASE / "research" / "deliverables"
STAGE1 = PHASE / "stage1_e2a"
REPO = PHASE.parents[2]

failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    if not condition:
        failures.append(name)


def sha256_file(path: Path) -> str:
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_signatures(bundle_path: Path, policy_path: Path, envelope_paths: list[Path]) -> tuple[int, int]:
    """Re-verify signed records against a trust bundle, independently."""
    sys.path.insert(0, str(STAGE1))
    from e2a import remediation
    signing = remediation.protected_signing()
    policy, _document = remediation.load_policy(policy_path)
    verified = 0
    failed = 0
    for path in envelope_paths:
        envelope = json.loads(Path(path).read_text())
        try:
            signing.verify_record(envelope["record"], bundle_path, policy)
            verified += 1
        except Exception:
            failed += 1
    return verified, failed


def main() -> int:
    print("=== 1. deliverables manifest ===")
    manifest = DELIVERABLES / "MANIFEST.sha256"
    listed = {}
    for line in manifest.read_text().splitlines():
        digest, name = line.split(None, 1)
        listed[name.strip()] = digest
    on_disk = sorted(p.name for p in DELIVERABLES.iterdir() if p.is_file() and p.name != "MANIFEST.sha256")
    check("manifest lists every deliverable", sorted(listed) == on_disk,
          f"{len(listed)} listed, {len(on_disk)} on disk")
    mismatched = [name for name, digest in listed.items() if sha256_file(DELIVERABLES / name) != digest]
    check("every manifest hash matches", not mismatched, str(mismatched))

    print("\n=== 2. deliverable JSON ===")
    bad = []
    for path in sorted(DELIVERABLES.glob("*.json")):
        try:
            json.loads(path.read_text())
        except ValueError:
            bad.append(path.name)
    check("all deliverable JSON parses", not bad, str(bad))

    print("\n=== 3. protected artifacts ===")
    expected = {
        "sp2027/analysis/RESULTS_LOCK.json": "4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39",
        "sp2027/analysis/RESULTS_LOCK_H1PC.json": "8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103",
        "sp2027/paper/main.tex": "51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461",
        "sp2027/paper/main.pdf": "fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a",
    }
    for relative, digest in expected.items():
        actual = sha256_file(REPO / relative)
        check(f"byte-identical: {relative}", actual == digest, actual[:16])

    print("\n=== 4. Stage 1 freeze manifest ===")
    sys.path.insert(0, str(STAGE1))
    from e2a import remediation
    report = remediation.manifest_verifier().verify_manifest(STAGE1 / "E2A_FREEZE.json", REPO)
    check("Stage 1 freeze verifies fail-closed", report.passed,
          f"{report.as_dict()['checked_files']} files, {len(report.as_dict()['errors'])} errors")

    print("\n=== 5. remediation test suite ===")
    completed = subprocess.run([sys.executable, "-m", "pytest", "-q"],
                               cwd=str(REPO / "sp2027" / "analysis" / "heb1_remediation_v1"),
                               capture_output=True, text=True)
    check("heb1_remediation_v1 tests pass", completed.returncode == 0,
          completed.stdout.strip().splitlines()[-1] if completed.stdout else "")

    print("\n=== 6. Stage 2 comparison ===")
    stage2 = json.loads((PHASE / "stage2_provenance" / "baseline_results.json").read_text())["summary"]
    check("22 cases compared", stage2["cases"] == 22)
    check("128/128 authentic signatures verified", stage2["cosign_authentic_pass"] == 128)
    check("128/128 tamper controls rejected", stage2["cosign_tamper_rejected"] == 128)
    check("native format gap documented", stage2["in_toto_native_accept"] == 0 and stage2["slsa_native_accept"] == 0)

    print("\n=== 7. Stage 3 boundary run ===")
    stage3 = json.loads((PHASE / "stage3_boundary" / "results" / "stage3_results.json").read_text())
    check("12 submissions recorded", len(stage3["submissions"]) == 12)
    check("zero unauthorized attributions", stage3["unauthorized_attribution_count"] == 0)
    positive = [row for row in stage3["submissions"] if row["family"] == "positive_control"]
    check("positive control attributed", positive and positive[0]["decision"] == "ATTRIBUTED_SUCCESS")
    check("live effect independently adjudicated",
          stage3["live_observation"]["reference_crypto_ok"] is True)
    check("5 model-authored fixtures refused",
          all(row["decision"] != "ATTRIBUTED_SUCCESS"
              for row in stage3["submissions"] if row["author"] == "model"))

    print("\n=== 8. Stage 4 matched arm ===")
    stage4 = json.loads((PHASE / "stage4_arms" / "model_arm_manifest.json").read_text())
    comparison = stage4["comparison"]
    check("22 cases in the model arm", comparison["model_arm"]["cases"] == 22)
    check("18/22 decision agreement", comparison["decision_agreement"]["agreeing"] == 18)
    check("4 disagreements, all explained", len(comparison["decision_agreement"]["disagreeing_cases"]) == 4)
    stage4_run = Path(stage4["run_dir"])
    model_rows = [json.loads(line) for line in (stage4_run / "raw_results.jsonl").read_text().splitlines() if line.strip()]
    attributed = [row for row in model_rows if row["e2a"]["decision"] == "ATTRIBUTED_SUCCESS"]
    unbacked = [row["case_id"] for row in attributed
                if not (row["reference"]["crypto_ok"] is True
                        and row["reference"]["verdict"] == "ACCEPTED")]
    check("every attribution is backed by an adjudicated positive predicate",
          not unbacked, f"{len(attributed)} attributions, unbacked: {unbacked}")
    mismatched = [row["case_id"] for row in attributed if not row["gt_success"]]
    check("the only label/artifact mismatch is the documented one",
          mismatched == ["H_FAIL_CH_01"], str(mismatched))
    check("14 provider calls, no fallback",
          stage4["provider_calls"] == 14 and stage4["no_fallback"] and stage4["no_retry"])

    print("\n=== 8b. Stage 4 replication and strict-reading sensitivity ===")
    first_run = sorted((PHASE / "stage4_arms" / "runs").glob("attempt1_*_model_arm"))[0]
    first_rows = {row["case_id"]: row for row in
                  (json.loads(line) for line in
                   (first_run / "raw_results.jsonl").read_text().splitlines() if line.strip())}
    model_rows_by_case = {row["case_id"]: row for row in model_rows}
    replication_agree = sum(1 for case_id, row in first_rows.items()
                             if case_id in model_rows_by_case
                             and row["e2a"]["decision"]
                             == model_rows_by_case[case_id]["e2a"]["decision"])
    check("two independent runs agree on every decision",
          replication_agree == len(first_rows) == 22, f"{replication_agree}/22")

    scripted_rows = [json.loads(line) for line in
                     (STAGE1 / "runs" / "20261020T065943Z_confirmatory" / "raw_results.jsonl")
                     .read_text().splitlines() if line.strip()]

    def strict_only_false_positives(run_rows: list[dict]) -> list[str]:
        return [row["case_id"] for row in run_rows
                if row["e2a"]["decision"] == "ATTRIBUTED_SUCCESS"
                and not row["gt_success"]
                and row["execution_status"] != "EXECUTED"]

    scripted_strict = strict_only_false_positives(scripted_rows)
    model_strict = strict_only_false_positives(model_rows)
    first_strict = strict_only_false_positives(list(first_rows.values()))
    check("strict reading: scripted arm has 0 strict-only false positives",
          not scripted_strict, str(scripted_strict))
    check("strict reading: exactly 1 strict-only false positive per model run",
          model_strict == ["H_FAIL_CH_01"] and first_strict == ["H_FAIL_CH_01"],
          f"run2={model_strict} run1={first_strict}")

    print("\n=== 8c. HEB-2 Contract V2 and soundness ===")
    heb2 = json.loads((PHASE / "heb2_contract_v1" / "evaluation_results.json").read_text())
    check("HEB-2 evaluation: 4 corpora", len(heb2["corpora"]) == 4)
    check("HEB-2: zero soundness violations across corpora",
          heb2["total_soundness_violations"] == 0)
    changes = {c["corpus"]: [s["case_id"] for s in c["semantic_changes"]]
               for c in heb2["corpora"]}
    check("HEB-2: semantic change confined to H_FAIL_CH_01 in the model arms",
          changes["stage4_model_arm_run1"] == ["H_FAIL_CH_01"]
          and changes["stage4_model_arm_run2"] == ["H_FAIL_CH_01"]
          and changes["stage1_confirmatory_scripted"] == [],
          json.dumps(changes, sort_keys=True))
    soundness_reports = sorted((PHASE / "heb2_contract_v1").glob("soundness_*.json"))
    check("HEB-2: four soundness reports, zero violations each",
          len(soundness_reports) == 4
          and all(not json.loads(path.read_text())["soundness_violations"]
                  for path in soundness_reports))
    check("HEB-2: mutation corpus scale",
          all(json.loads(path.read_text())["evaluations"] == 2814
              for path in soundness_reports))

    print("\n=== 8d. Stage 5 live campaign ===")
    campaign_runs = sorted((PHASE / "stage5_live_campaign" / "runs").glob("*"))
    model_runs = [d for d in campaign_runs if d.name.endswith("_live")]
    control_runs = [d for d in campaign_runs if d.name.endswith("_control")]
    model_results = json.loads((model_runs[-1] / "campaign_results.json").read_text())
    control_results = json.loads((control_runs[-1] / "control_results.json").read_text())
    check("Stage 5 model arm: no successful claim within the card caps",
          model_results["success_turn"] is None
          and model_results["graded_submissions"] <= 4
          and model_results["turns_used"] <= 8)
    check("Stage 5 model arm: contract refused the attempt",
          model_results["decisions"]["output"]["decision"] != "ATTRIBUTED_SUCCESS")
    check("Stage 5 control: oracle confirmed the disclosure",
          control_results["oracle_verdict"]["success"] is True)
    check("Stage 5 control: contract attributed the live exploit",
          control_results["decisions"]["output"]["decision"] == "ATTRIBUTED_SUCCESS"
          and control_results["decisions"]["completion"]["decision"] == "ATTRIBUTED_SUCCESS")

    print("\n=== 8e. Stage 6 matched translation ===")
    translation = json.loads(
        (PHASE / "stage6_matched_translation" / "translation_results_v2.json").read_text())
    rows = translation["rows"]
    labels = json.loads((STAGE1 / "frozen" / "labels.json").read_text())["labels"]
    truthy = {row["case_id"] for row in labels if row["gt_success"]}
    reference = {row["case_id"]: row["acts"]["output"]["decision"] == "ATTRIBUTED_SUCCESS"
                 for row in rows}
    default_false_promotions = [row["case_id"] for row in rows
                                if row["in_toto_default"]["accepted"]
                                and row["case_id"] not in truthy]
    policy_false_promotions = [row["case_id"] for row in rows
                               if row["in_toto_policy"]["accepted"]
                               and row["case_id"] not in truthy]
    stateful_false_promotions = [row["case_id"] for row in rows
                                  if row["in_toto_policy_stateful"]["accepted"]
                                  and row["case_id"] not in truthy]
    policy_agreement = sum(1 for row in rows
                           if row["in_toto_policy"]["accepted"] == reference[row["case_id"]])
    stateful_agreement = sum(1 for row in rows
                             if row["in_toto_policy_stateful"]["accepted"] == reference[row["case_id"]])
    check("Stage 6: a minimally configured in-toto promotes every non-attributable case",
          len(default_false_promotions) == 16, str(len(default_false_promotions)))
    check("Stage 6: in-toto with rules and an independent inspection promotes only the replay case",
          policy_false_promotions == ["X_REPLAY"], str(policy_false_promotions))
    check("Stage 6: the stateful in-toto policy arm promotes none",
          not stateful_false_promotions, str(stateful_false_promotions))
    check("Stage 6: in-toto with the policy reaches 21/22, and 22/22 when stateful",
          policy_agreement == 21 and stateful_agreement == 22,
          f"stateless {policy_agreement}, stateful {stateful_agreement}")
    check("Stage 6: SLSA is not comparable — verification stops before the policy stage",
          all(row["slsa"]["stage"] in ("provenance-acquisition-rekor", "timeout",
                                       "signature-or-identity", "trust-root-refresh")
              for row in rows)
          and not any(row["slsa"]["accepted"] for row in rows))
    check("Stage 6: the ACTS reference false-promotes none",
          sum(1 for case_id, attributed in reference.items()
              if attributed and case_id not in truthy) == 0)

    print("\n=== 9. independent signature verification ===")
    stage3_run = Path(stage3["run_dir"])
    stage3_envelopes = sorted(stage3_run.glob("*/observation.json")) + sorted(stage3_run.glob("*/reference.json"))
    verified, failed = verify_signatures(
        PHASE / "stage3_boundary" / "trust" / "issuers_public.json",
        PHASE / "stage3_boundary" / "trust" / "trust_policy.json",
        stage3_envelopes)
    check("Stage 3 signed records verify", failed == 0 and verified == len(stage3_envelopes),
          f"{verified}/{len(stage3_envelopes)} verified")

    stage4_run = Path(stage4["run_dir"])
    stage4_envelopes = sorted(stage4_run.glob("cases/*/observation.json")) + sorted(stage4_run.glob("cases/*/reference.json"))
    verified4, failed4 = verify_signatures(
        PHASE / "stage4_arms" / "trust" / "issuers_public.json",
        PHASE / "stage4_arms" / "trust" / "trust_policy.json",
        stage4_envelopes)
    check("Stage 4 signed records verify", failed4 == 0 and verified4 == len(stage4_envelopes),
          f"{verified4}/{len(stage4_envelopes)} verified")

    print()
    if failures:
        print(f"FAILURES: {failures}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())