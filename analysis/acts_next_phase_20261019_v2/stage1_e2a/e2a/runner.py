"""Single frozen execution of the E2A case inventory.

One run.  Every attempted case is preserved, including failures.  Raw
stdout/stderr/return codes are retained per case.  The results file is
append-only and is the authoritative record.

Trust boundary
--------------
* the TEO and the reference adjudicator run as **separate processes**;
* the aggregator runs in-process because the replay ledger is deliberately an
  explicit in-memory state (E2A_PREREGISTRATION 9.5);
* the baseline invokes the frozen Stage 01 components as unmodified
  subprocesses.

Nothing in this module contacts the network or a model provider.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):  # pragma: no cover - direct execution support
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from e2a import baseline, canonical, cases, producers, remediation
    from e2a.aggregator import Aggregator
else:
    from . import baseline, canonical, cases, producers, remediation
    from .aggregator import Aggregator

STAGE1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = STAGE1_ROOT.parents[3]
DOMAIN = canonical.DOMAIN


# --------------------------------------------------------------------------
# process helpers
# --------------------------------------------------------------------------

def _child_env() -> dict[str, str]:
    environment = dict(os.environ)
    existing = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = f"{STAGE1_ROOT}{os.pathsep}{existing}" if existing else str(STAGE1_ROOT)
    return environment


def run_json_command(command: list[str], payload: dict[str, Any] | None = None,
                     out_path: Path | None = None) -> dict[str, Any]:
    """Run a component subprocess and return its parsed stdout."""
    completed = subprocess.run(
        command, cwd=str(STAGE1_ROOT), env=_child_env(), text=True,
        capture_output=True, check=False,
        input=(json.dumps(payload) if payload is not None else None))
    if completed.returncode != 0:
        raise RuntimeError(f"{command} failed: {completed.stderr.strip()[:800]}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"{command} produced unparsable output: {exc}") from exc


# --------------------------------------------------------------------------
# component invocations
# --------------------------------------------------------------------------

def build_instance(task: str, seed: int) -> dict[str, Any]:
    generator = remediation.stage01_generator()
    if task == "ECDSA_Nonce_Reuse":
        return generator.make_ecdsa(seed)
    if task == "ChaCha20_Nonce_Repeat":
        return generator.make_chacha(seed)
    raise ValueError(f"unknown task {task!r}")


def public_instance(instance: dict[str, Any], condition: str) -> dict[str, Any]:
    if condition == "C1":
        return instance["c1"]
    if condition == "C2":
        return instance["c2"]
    if condition == "C0":
        return instance["c0"]
    raise ValueError(f"unknown condition {condition!r}")


def private_target_state(task: str, instance: dict[str, Any]) -> dict[str, Any]:
    return {"primitive": task, **instance["semantic"]}


def context_for(kind: str, role: str, target_id: str, attempt_id: str, epoch: int) -> dict[str, Any]:
    return {
        "kind": kind,
        "domain": DOMAIN,
        "target_id": target_id,
        "attempt_id": attempt_id,
        "epoch": epoch,
        "role": role,
    }


def run_teo(case_dir: Path, case_id: str, task: str, seed: int, condition: str, variant: str,
            target_id: str, attempt_id: str, epoch: int, keys_dir: Path, bundle_path: Path,
            policy_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the trusted execution observer in its own process."""
    instance = build_instance(task, seed)
    public = public_instance(instance, condition)
    source_text = producers.produce_source(task, variant)
    spec = {
        "case_id": case_id,
        "case_dir": str(case_dir),
        "producer": {**producers.producer_identity(case_id),
                     "producer_nonce": producers.producer_nonce(case_id, task, seed, variant)},
        "program_source_text": source_text,
        "public_instance": public,
        "target_id": target_id,
        "attempt_id": attempt_id,
        "epoch": epoch,
        "context": context_for(canonical.OBSERVATION_KIND, remediation.ROLE_OBSERVER,
                               target_id, attempt_id, epoch),
    }
    spec_path = case_dir / "spec_observer.json"
    spec_path.write_text(json.dumps(spec, sort_keys=True, indent=2) + "\n")
    out_path = case_dir / "observation.json"
    run_json_command([sys.executable, "-m", "e2a.observer", "--spec", str(spec_path),
                      "--out", str(out_path), "--keys", str(keys_dir),
                      "--bundle", str(bundle_path), "--policy", str(policy_path)])
    envelope = json.loads(out_path.read_text(encoding="utf-8"))
    return envelope, instance


def run_reference(case_dir: Path, case_id: str, task: str, seed: int, condition: str,
                  observation_envelope: dict[str, Any], observation_path: Path,
                  target_id: str, attempt_id: str, epoch: int, keys_dir: Path,
                  bundle_path: Path, policy_path: Path) -> dict[str, Any]:
    """Run the trusted reference adjudicator in its own process."""
    instance = build_instance(task, seed)
    public = public_instance(instance, condition)
    payload = observation_envelope["record"]["payload"]
    stdout_path = payload.get("stdout_path")
    stdout_bytes = Path(stdout_path).read_bytes() if stdout_path else b""
    spec = {
        "case_id": case_id,
        "observation_path": str(observation_path),
        "stdout_hex": stdout_bytes.hex(),
        "public_instance": public,
        "target_state": private_target_state(task, instance),
        "target_id": target_id,
        "attempt_id": attempt_id,
        "epoch": epoch,
        "context": context_for(canonical.REFERENCE_KIND, remediation.ROLE_REFERENCE,
                               target_id, attempt_id, epoch),
    }
    spec_path = case_dir / "spec_reference.json"
    spec_path.write_text(json.dumps(spec, sort_keys=True, indent=2) + "\n")
    out_path = case_dir / "reference.json"
    run_json_command([sys.executable, "-m", "e2a.reference", "--spec", str(spec_path),
                      "--out", str(out_path), "--keys", str(keys_dir),
                      "--bundle", str(bundle_path), "--policy", str(policy_path)])
    return json.loads(out_path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# certificate assembly (the untrusted assembly layer)
# --------------------------------------------------------------------------

def assemble_e2a_certificate(case_id: str, target_id: str, attempt_id: str, epoch: int,
                              observation: dict[str, Any], reference: dict[str, Any],
                              artifact_path: Path, artifact_sha256: str,
                              candidate_path: Path, candidate_sha256: str,
                              include_observation: bool = True,
                              include_reference: bool = True,
                              claims_attribution: str = "PROVEN") -> dict[str, Any]:
    """Assemble the certificate that is presented to the aggregator.

    The claimant's ``claims`` block is *declarative only*.  The aggregator
    never reads it when deciding.
    """
    evidence: dict[str, Any] = {}
    if include_observation:
        evidence["observation"] = observation
    if include_reference:
        evidence["reference"] = reference
    return {
        "schema": "e2a-attribution-certificate/1",
        "case_id": case_id,
        "target_id": target_id,
        "attempt_id": attempt_id,
        "epoch": epoch,
        "agent_artifact": {"path": str(artifact_path), "sha256": artifact_sha256, "language": "python"},
        "candidate_output": {"path": str(candidate_path), "sha256": candidate_sha256},
        "claims": {
            "attribution": claims_attribution,
            "artifact_authorship": "PROVEN",
            "execution_identity": "PROVEN",
            "target_effect": "OBSERVED",
            "boundary_enforcement": "PROVEN",
            "reference_oracle_acceptance": "ACCEPTED",
        },
        "evidence": evidence,
    }


# --------------------------------------------------------------------------
# baseline construction
# --------------------------------------------------------------------------

def run_baseline(baseline_dir: Path, case: dict[str, Any], session_id: str, base_id: str,
                 artifact_path: Path, target_status: str, candidate_file: Path,
                 target_state: dict[str, Any], task: str, condition: str, seed: int,
                 claims_attribution: str | None = None) -> dict[str, Any]:
    """Build the Stage 01 certificate and invoke the frozen components."""
    baseline_dir.mkdir(parents=True, exist_ok=True)
    certificate = baseline.make_certificate(
        baseline_dir, session_id, base_id, task, condition, seed, artifact_path, target_status)
    if claims_attribution is not None:
        certificate["claims"]["attribution"] = claims_attribution
    certificate_path = baseline_dir / "certificate.private.json"
    baseline.write_json(certificate_path, certificate)
    baseline.write_json(baseline_dir / "target_state.private.json", target_state)

    # The frozen reference verifier consumes a candidate output *file*.
    candidate_copy = baseline_dir / "candidate_output.json"
    candidate_copy.write_bytes(Path(candidate_file).read_bytes())
    bundle_path = baseline_dir / "reference_input.json"
    baseline.write_json(bundle_path, {
        "case_id": session_id,
        "target_state_path": str(baseline_dir / "target_state.private.json"),
        "candidate_path": str(candidate_copy),
        "certificate_path": str(certificate_path),
    })

    public = baseline.public_certificate(certificate)
    validator = baseline.run_frozen_validator(public)
    reference = baseline.run_frozen_reference({"_bundle_path": bundle_path})
    return {
        "validator": validator,
        "reference": reference,
        "target_status": target_status,
        "certificate_path": str(certificate_path),
        "public_certificate_path": str(baseline_dir / "certificate.public.json"),
        "bundle_path": str(bundle_path),
        "public_certificate": public,
    }


# --------------------------------------------------------------------------
# main run
# --------------------------------------------------------------------------

def execute_run(run_dir: Path, keys_dir: Path, trust_dir: Path) -> dict[str, Any]:
    bundle_path = trust_dir / "issuers_public.json"
    policy_path = trust_dir / "trust_policy.json"
    run_dir.mkdir(parents=True, exist_ok=True)
    cases_root = run_dir / "cases"
    cases_root.mkdir(parents=True, exist_ok=True)

    aggregator = Aggregator(bundle_path, policy_path, run_dir / "replay_ledger.jsonl")
    raw_path = run_dir / "raw_results.jsonl"
    if raw_path.exists():
        raw_path.unlink()

    rows: list[dict[str, Any]] = []
    prior_artifacts: dict[str, Any] = {}

    for ordinal, case in enumerate(cases.CASES, start=1):
        case_id = case["case_id"]
        case_dir = cases_root / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        task, seed = case["task"], case["seed"]
        condition = case["condition"]
        target_id = f"{task}-seed-{seed:02d}"
        attempt_id = f"e2a-{case_id}"
        epoch = 1
        attack = case["attack"]

        # -- declared attempt / context may be perturbed by an attack -------
        declared_target_id = target_id
        declared_attempt_id = attempt_id
        declared_epoch = epoch
        observation_attempt_id = attempt_id
        observation_target_id = target_id

        if attack == "stale_attempt":
            observation_attempt_id = f"{attempt_id}-A"
            declared_attempt_id = f"{attempt_id}-B"
        if attack == "context_conflict":
            observation_target_id = f"{target_id}-other"
            declared_target_id = f"{target_id}-other"
            declared_attempt_id = f"{attempt_id}-B"
            declared_epoch = 2

        # -- main execution ---------------------------------------------------
        observation, instance = run_teo(
            case_dir, case_id, task, seed, condition, case["producer_variant"],
            observation_target_id, observation_attempt_id, epoch,
            keys_dir, bundle_path, policy_path)
        observation_payload = observation["record"]["payload"]

        reference = run_reference(
            case_dir, case_id, task, seed, condition, observation,
            case_dir / "observation.json", observation_target_id, observation_attempt_id,
            epoch, keys_dir, bundle_path, policy_path)
        reference_payload = reference["record"]["payload"]

        artifact_path = Path(observation_payload["program_source_artifact_path"])
        candidate_path = case_dir / "candidate_output.json"
        stdout_path = observation_payload.get("stdout_path")
        if stdout_path:
            try:
                candidate_path.write_bytes(Path(stdout_path).read_bytes())
            except FileNotFoundError:
                pass
        candidate_sha = observation_payload["parse"]["parsed_candidate_sha256"]
        if candidate_sha is None:
            candidate_path = case_dir / "candidate_output.absent.json"
            candidate_path.write_bytes(b"")
            candidate_sha = canonical.sha_bytes(b"")

        # -- attack-specific construction -------------------------------------
        declared_artifact_path = artifact_path
        declared_artifact_sha = observation_payload["program_source_sha256"]
        baseline_candidate_file = candidate_path
        presented_observation, presented_reference = observation, reference
        swap_run: dict[str, Any] | None = None

        if attack == "identity_swap":
            other_source = producers.produce_source(task, "correct" if case["producer_variant"] != "correct" else "wrong")
            declared_artifact_path = case_dir / "declared_artifact.py"
            declared_artifact_path.write_text(other_source)
            declared_artifact_sha = canonical.sha_bytes(other_source.encode("utf-8"))

        if attack in {"output_swap", "reference_mismatch"}:
            swap_dir = case_dir / "swap_run"
            swap_dir.mkdir(parents=True, exist_ok=True)
            swap_variant = "correct" if case["producer_variant"] == "wrong" else "wrong"
            swap_observation, swap_instance = run_teo(
                swap_dir, f"{case_id}-swap", task, seed, condition, swap_variant,
                target_id, attempt_id, epoch, keys_dir, bundle_path, policy_path)
            swap_reference = run_reference(
                swap_dir, f"{case_id}-swap", task, seed, condition, swap_observation,
                swap_dir / "observation.json", target_id, attempt_id, epoch,
                keys_dir, bundle_path, policy_path)
            swap_payload = swap_reference["record"]["payload"]
            swap_candidate_out = swap_dir / "candidate_output.json"
            swap_stdout_path = swap_observation["record"]["payload"].get("stdout_path")
            if swap_stdout_path:
                try:
                    swap_candidate_out.write_bytes(Path(swap_stdout_path).read_bytes())
                except FileNotFoundError:
                    swap_candidate_out.write_bytes(b"")
            swap_run = {
                "dir": str(swap_dir),
                "observation": str(swap_dir / "observation.json"),
                "reference": str(swap_dir / "reference.json"),
                "crypto_ok": swap_payload["crypto_ok"],
                "stdout_sha256": swap_payload["stdout_sha256"],
            }
            baseline_candidate_file = swap_dir / "candidate_output.json"
            if attack == "output_swap":
                # The certificate declares a candidate output that the observer
                # did not produce.
                candidate_sha = swap_payload["candidate_digest"]
            else:
                # The presented reference record is the one produced for the
                # *other* execution.
                presented_reference = swap_reference

        if attack == "replay":
            source_case = "H_OK_EC_01"
            source_dir = cases_root / source_case
            source_observation = json.loads((source_dir / "observation.json").read_text(encoding="utf-8"))
            presented_observation = source_observation
            presented_reference = json.loads((source_dir / "reference.json").read_text(encoding="utf-8"))
            declared_target_id = source_observation["context"]["target_id"]
            declared_attempt_id = source_observation["context"]["attempt_id"]
            declared_epoch = source_observation["context"]["epoch"]

        # -- E2A evaluation ----------------------------------------------------
        certificate = assemble_e2a_certificate(
            case_id, declared_target_id, declared_attempt_id, declared_epoch,
            presented_observation, presented_reference,
            declared_artifact_path, declared_artifact_sha, candidate_path, candidate_sha,
            include_observation=(attack != "omit_observation"),
            include_reference=(attack != "omit_reference"),
        )
        certificate_path = case_dir / "certificate.e2a.json"
        certificate_path.write_text(json.dumps(certificate, sort_keys=True, indent=2) + "\n")

        bundle = {"case_id": case_id, "certificate": certificate}
        decision = aggregator.evaluate(bundle)

        # -- S1: declaration sensitivity --------------------------------------
        flipped = json.loads(json.dumps(certificate))
        flipped["claims"]["attribution"] = "NOT_ESTABLISHED"
        clone_a = aggregator.clone_for_sensitivity_check()
        clone_b = aggregator.clone_for_sensitivity_check()
        decision_a = clone_a.evaluate({"case_id": case_id, "certificate": certificate})
        decision_b = clone_b.evaluate({"case_id": case_id, "certificate": flipped})
        s1 = {
            "claim_proven": decision_a["decision"],
            "claim_not_established": decision_b["decision"],
            "changed": decision_a["decision"] != decision_b["decision"],
        }

        claim = aggregator.sign_claim(certificate, decision, keys_dir)
        (case_dir / "claim.e2a.json").write_text(json.dumps(claim, sort_keys=True, indent=2) + "\n")

        # -- baseline ----------------------------------------------------------
        execution_status = baseline.stage01_execution_status(observation_payload)
        historical_output = (observation_payload.get("parse") or {}).get("parsed_candidate_lastline")
        target_status = baseline.stage01_target_status(execution_status, condition, historical_output)
        baseline_dir = case_dir / "baseline"
        baseline_artifact = artifact_path
        if attack == "identity_swap":
            baseline_artifact = declared_artifact_path
        baseline_session = session_id_for(case_id, attempt=declared_attempt_id)
        baseline_base_id = declared_target_id
        baseline_result = run_baseline(
            baseline_dir, case, baseline_session, baseline_base_id, baseline_artifact,
            target_status, baseline_candidate_file, private_target_state(task, instance),
            task, condition, seed)
        baseline.write_json(Path(baseline_result["public_certificate_path"]),
                            baseline_result["public_certificate"])

        # S1 for the baseline: identical evidence, flipped claimant assertion.
        baseline_flipped = json.loads(json.dumps(baseline_result["public_certificate"]))
        baseline_flipped["claims"]["attribution"] = "NOT_ESTABLISHED"
        baseline_flipped_result = baseline.run_frozen_validator(baseline_flipped)
        baseline_s1 = {
            "claim_proven": baseline_result["validator"].get("decision"),
            "claim_not_established": baseline_flipped_result.get("decision"),
            "changed": baseline_result["validator"].get("decision") != baseline_flipped_result.get("decision"),
        }

        row = {
            "ordinal": ordinal,
            "case_id": case_id,
            "case_class": case["case_class"],
            "gt_success": case["gt_success"],
            "task": task,
            "seed": seed,
            "condition": condition,
            "producer_variant": case["producer_variant"],
            "attack": attack,
            "declared_context": {"target_id": declared_target_id,
                                 "attempt_id": declared_attempt_id, "epoch": declared_epoch},
            "observation_context": observation["context"],
            "execution_status": observation_payload["execution_status"],
            "screen": observation_payload["screen"],
            "parse_status": observation_payload["parse"]["parse_status"],
            "returncode": observation_payload.get("returncode"),
            "stdout_sha256": observation_payload.get("stdout_sha256"),
            "stderr_sha256": observation_payload.get("stderr_sha256"),
            "program_source_sha256": observation_payload["program_source_sha256"],
            "parsed_candidate_sha256": observation_payload["parse"]["parsed_candidate_sha256"],
            "reference": {
                "status": reference_payload["status"],
                "verdict": reference_payload["verdict"],
                "crypto_ok": reference_payload["crypto_ok"],
                "crypto_details": reference_payload["crypto_details"],
                "candidate_digest": reference_payload["candidate_digest"],
                "stdout_sha256": reference_payload["stdout_sha256"],
            },
            "e2a": {"decision": decision["decision"], "reason": decision["reason"],
                    "reason_family": decision["reason_family"]},
            "e2a_s1": s1,
            "baseline": {
                "execution_status": execution_status,
                "target_status": target_status,
                "validator": baseline_result["validator"],
                "reference_verdict": baseline_result["reference"].get("reference_verdict"),
                "reference_cryptographic_predicate": baseline_result["reference"].get("cryptographic_predicate"),
            },
            "baseline_s1": baseline_s1,
            "swap_run": swap_run,
            "artifacts": {
                "observation": str(case_dir / "observation.json"),
                "reference": str(case_dir / "reference.json"),
                "certificate_e2a": str(certificate_path),
                "claim_e2a": str(case_dir / "claim.e2a.json"),
                "baseline_certificate": baseline_result["certificate_path"],
                "stdout": observation_payload.get("stdout_path"),
                "stderr": observation_payload.get("stderr_path"),
            },
        }
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        rows.append(row)
        prior_artifacts[case_id] = {"case_dir": str(case_dir)}

    manifest = {
        "schema": "e2a-run-manifest/1",
        "run_dir": str(run_dir),
        "case_count": len(rows),
        "results_file": str(raw_path),
        "results_sha256": canonical.sha_file(raw_path),
        "trust_bundle": str(bundle_path),
        "policy": str(policy_path),
        "frozen_validator": str(baseline.FROZEN_VALIDATOR),
        "frozen_reference": str(baseline.FROZEN_REFERENCE),
        "model_calls": 0,
        "network_calls": 0,
        "provider_calls": 0,
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    return manifest


def session_id_for(case_id: str, attempt: str | None = None) -> str:
    return attempt or f"e2a-{case_id}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="E2A single frozen run")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--keys", type=Path, required=True)
    parser.add_argument("--trust", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    if args.run_dir.exists() and any(args.run_dir.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty run directory: {args.run_dir}")

    def _execute():
        return execute_run(args.run_dir, args.keys, args.trust)

    if args.manifest is not None:
        sys.path.insert(0, str(remediation.REMEDIATION_ROOT / "integrity"))
        import manifest_verifier  # type: ignore
        report = manifest_verifier.preflight_then_execute(args.manifest, args.repo_root, _execute)
        preflight = manifest_verifier.verify_manifest(args.manifest, args.repo_root).as_dict()
        (args.run_dir / "preflight_report.json").write_text(
            json.dumps(preflight, sort_keys=True, indent=2) + "\n")
    else:
        report = _execute()
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
