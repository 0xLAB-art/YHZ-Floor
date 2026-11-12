#!/usr/bin/env python3
"""Stage 1 (TOEEA-1) measurement runner.

One pass over the 27 frozen cases.  For each case the runner

  1. builds the frozen fixture and the candidate program,
  2. executes the program through the *trusted execution observer* (a party
     whose Ed25519 key the producer never holds),
  3. obtains an independent cryptographic verdict from the *reference
     verifier* (a second party, also holding a secret key),
  4. assembles the evidence bundle and applies the case's preregistered
     mutation,
  5. evaluates the bundle with the E0/E1/E2/E3 evaluator ladder, and
  6. where the case has a direct Stage01 analogue, runs the FROZEN historical
     Stage01 reference-verifier + blind-validator pair on the same execution.

Everything is local and offline.  No network call, no provider call, no
attacker capability is introduced beyond constructing the preregistered
contradiction conditions, which are *synthetic detection cases* and not
claims about a deployed service.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import s1_common  # noqa: F401  (importing it installs the remediation import paths)

from context_validator import ReplayState

from s1_attribution_evaluator import AttributionEvaluator, RunExpectation
from s1_baseline_evaluators import BASELINE_EVALUATORS
from s1_cases import CASE_SPECS, CaseSpec, build_program_source
from s1_common import (
    BUNDLE_SCHEMA,
    DECISION_INCONCLUSIVE,
    DECISION_REJECT,
    DECISION_SUCCESS,
    KIND_ARTIFACT_RECORD,
    KIND_EXECUTION_OBSERVATION,
    KIND_EXECUTION_STDERR,
    KIND_EXECUTION_STDOUT,
    KIND_PROGRAM_OUTPUT,
    KIND_PROGRAM_SOURCE,
    KIND_REFERENCE_VERDICT,
    ROLE_ARTIFACT_PRODUCER,
    SIGNING_CONTEXT,
    build_context,
    digest_object,
    issuer_policy,
    load_frozen_fixture_generator,
    read_json,
    sha256_bytes,
    sha256_file,
    sign_context_bytes,
    write_json,
)
from s1_reference_verifier import ReferenceVerifier
from s1_stage01_compat import (
    build_stage01_certificate,
    historical_target_status,
    run_frozen_stage01_pair,
)
from s1_trusted_observer import TrustedObserver
from s1_setup_trust import setup as setup_trust

STAGE1_ROOT = Path(__file__).resolve().parent
WORK_ROOT = STAGE1_ROOT / "work"
PRIVATE_ROOT = STAGE1_ROOT / "private"
RESULTS_ROOT = STAGE1_ROOT / "runs"
INVENTORY_ROOT = STAGE1_ROOT / "s1_case_inventory"
INTEGRITY_MANIFEST = STAGE1_ROOT / "s1_integrity_manifest.json"
EVALUATOR_NAMES = ("digest_only", "signed_digest_only", "signed_context_only", "full")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _canonical_signing_bytes(unsigned: dict[str, Any]) -> bytes:
    """Reproduce ``protected_signing``'s canonical unsigned form exactly."""
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _sign_raw(private_key, unsigned: dict[str, Any]) -> str:
    return private_key.sign(_canonical_signing_bytes(unsigned)).hex()


def _unsigned_of(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k != "signature_hex"}


def make_producer_record(key_path: Path, private_key, *, program_path: Path,
                         attempt_id: str, session_id: str, epoch: int,
                         target_id: str, program_sha256: str | None = None) -> dict[str, Any]:
    """Produce the artifact-producer's signed authorship record."""
    from protected_signing import SignRequest, sign_record

    facts = {
        "producer_id": "s1-scripted-artifact-producer",
        "program_path": program_path.name,
        "program_sha256": program_sha256 if program_sha256 is not None else sha256_file(program_path),
        "attempt_id": attempt_id,
        "session_id": session_id,
        "epoch": int(epoch),
        "target_id": target_id,
    }
    context = build_context(KIND_ARTIFACT_RECORD, ROLE_ARTIFACT_PRODUCER,
                            target_id, attempt_id, epoch)
    payload = {
        "context": context,
        "context_signature_hex": sign_context_bytes(private_key, context),
        "facts": facts,
    }
    return sign_record(
        key_path,
        SignRequest(kind=KIND_ARTIFACT_RECORD, context=SIGNING_CONTEXT, payload=payload),
        issuer_policy(),
    )


def resign_observation(observation: dict[str, Any], private_key, *, epoch: int | None = None,
                       attempt_id: str | None = None) -> dict[str, Any]:
    """Re-sign an existing observation record under a different epoch/attempt.

    The facts are preserved verbatim; only the signed context binding changes.
    This models an observer (or a party replaying an observer's record) that
    presents the observation against the wrong freshness/target binding.
    """
    record = json.loads(json.dumps(observation))
    facts = record["payload"]["facts"]
    context = dict(record["payload"]["context"])
    if epoch is not None:
        context["epoch"] = int(epoch)
        facts = dict(facts)
        facts["epoch"] = int(epoch)
    if attempt_id is not None:
        context["attempt_id"] = attempt_id
        facts = dict(facts)
        facts["attempt_id"] = attempt_id
    payload = {
        "context": context,
        "context_signature_hex": sign_context_bytes(private_key, context),
        "facts": facts,
    }
    unsigned = {
        "format": record["format"],
        "domain": record["domain"],
        "kind": record["kind"],
        "context": record["context"],
        "issuer_role": record["issuer_role"],
        "key_id": record["key_id"],
        "payload": payload,
    }
    unsigned["signature_hex"] = _sign_raw(private_key, unsigned)
    return unsigned


def forge_observation_with_producer_key(observation: dict[str, Any], producer_key_path: Path,
                                        producer_private_key) -> dict[str, Any]:
    """Re-sign an observer record with the PRODUCER key, keeping the role claim.

    The resulting record has a *valid* signature under a registered key, but
    that key's registered role is ``artifact_producer`` while the record
    claims ``execution_observer``.  Only a role-authorized verifier can
    detect this.
    """
    from protected_signing import load_private_key

    key_id, _role, _key = load_private_key(producer_key_path)
    record = json.loads(json.dumps(observation))
    unsigned = _unsigned_of(record)
    unsigned["key_id"] = key_id
    unsigned["issuer_role"] = "execution_observer"
    unsigned["signature_hex"] = _sign_raw(producer_private_key, unsigned)
    return unsigned


def historical_execution_status(returncode: Any, output_parsed: bool) -> str:
    """Mirror ``run_contract_sound_agent_pilot.execute_candidate`` status logic."""
    if returncode is None:
        return "EXECUTION_FAILED"
    if returncode != 0:
        return "EXECUTION_FAILED"
    if not output_parsed:
        return "MALFORMED_OUTPUT"
    return "EXECUTED"


# ---------------------------------------------------------------------------
# case preparation
# ---------------------------------------------------------------------------
def _fixture_for(spec: CaseSpec) -> tuple[dict[str, Any], dict[str, Any]]:
    fx = load_frozen_fixture_generator()
    if spec.primitive == "ECDSA_Nonce_Reuse":
        fixture = fx.make_ecdsa(spec.seed)
    elif spec.primitive == "ChaCha20_Nonce_Repeat":
        fixture = fx.make_chacha(spec.seed)
    else:  # pragma: no cover - defensive
        raise ValueError(f"unknown primitive {spec.primitive}")
    instance = fixture[spec.condition.lower()]  # "c1" or "c0"
    return fixture, instance


def _private_target(spec: CaseSpec, fixture: dict[str, Any]) -> Path:
    PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
    path = PRIVATE_ROOT / spec.case_id / "target_state.json"
    target = {"primitive": spec.primitive, **fixture["semantic"]}
    write_json(path, target)
    return path


def _inventory_dir(spec: CaseSpec) -> Path:
    return INVENTORY_ROOT / "cases" / spec.case_id


def _prepare_case(spec: CaseSpec, case_dir: Path) -> dict[str, Any]:
    """Materialise the program, the public instance and the private target.

    The program bytes and the public instance are copied from the **frozen
    case inventory** (``s1_case_inventory/``), which is hash-pinned by the
    integrity manifest.  The private target state is a deterministic function
    of the frozen fixture generator and the seed, both of which are hash-pinned
    as well, so it is regenerated here and never enters the public inventory.
    """
    fixture, instance = _fixture_for(spec)
    program_dir = case_dir / "program"
    program_dir.mkdir(parents=True, exist_ok=True)

    inv = _inventory_dir(spec)
    inv_program = inv / "candidate.py"
    inv_instance = inv / "public_instance.json"
    if not inv_program.is_file() or not inv_instance.is_file():
        raise FileNotFoundError(
            f"frozen case inventory incomplete for {spec.case_id}; "
            "run s1_make_cases.py before the freeze"
        )
    frozen_instance = json.loads(inv_instance.read_text())
    if frozen_instance != instance:
        raise RuntimeError(
            f"frozen instance for {spec.case_id} does not match the regenerated "
            "fixture; the case inventory and the frozen fixture generator have "
            "diverged"
        )

    program_path = program_dir / "candidate.py"
    program_path.write_bytes(inv_program.read_bytes())
    instance_path = program_dir / "public_instance.json"
    instance_path.write_bytes(inv_instance.read_bytes())

    target_path = _private_target(spec, fixture)
    return {
        "fixture": fixture,
        "instance": instance,
        "program_path": program_path,
        "instance_path": instance_path,
        "target_path": target_path,
    }


# ---------------------------------------------------------------------------
# bundle assembly
# ---------------------------------------------------------------------------
def _bundle_entries(case_dir: Path) -> list[dict[str, Any]]:
    layout = [
        (KIND_ARTIFACT_RECORD, "artifact_record.json"),
        (KIND_EXECUTION_OBSERVATION, "observation.json"),
        (KIND_REFERENCE_VERDICT, "reference_verdict.json"),
        (KIND_PROGRAM_SOURCE, "program/candidate.py"),
        (KIND_PROGRAM_OUTPUT, "execution/candidate_output.json"),
        (KIND_EXECUTION_STDOUT, "execution/executor_stdout.txt"),
        (KIND_EXECUTION_STDERR, "execution/executor_stderr.txt"),
    ]
    entries = []
    for kind, rel in layout:
        abs_path = case_dir / rel
        if not abs_path.exists():
            continue
        entries.append({
            "kind": kind,
            "path": rel,
            "sha256": sha256_file(abs_path),
        })
    return entries


def _write_bundle(case_dir: Path, run_block: dict[str, Any], entries: list[dict[str, Any]]) -> Path:
    bundle = {
        "schema": BUNDLE_SCHEMA,
        "run": run_block,
        "entries": entries,
    }
    path = case_dir / "bundle.json"
    write_json(path, bundle)
    return path


def _entry(bundle: dict[str, Any], kind: str) -> dict[str, Any] | None:
    for entry in bundle.get("entries", []):
        if entry.get("kind") == kind:
            return entry
    return None


def _drop_entry(bundle: dict[str, Any], kind: str) -> None:
    bundle["entries"] = [e for e in bundle.get("entries", []) if e.get("kind") != kind]


def _refresh_entry_digest(bundle: dict[str, Any], bundle_root: Path, kind: str) -> None:
    for entry in bundle.get("entries", []):
        if entry.get("kind") == kind:
            entry["sha256"] = sha256_file(bundle_root / entry["path"])


# ---------------------------------------------------------------------------
# main case loop
# ---------------------------------------------------------------------------
def run_case(spec: CaseSpec, trust: dict[str, Any], observer_key, observer_priv,
             producer_key, producer_priv, reference_key) -> dict[str, Any]:
    case_dir = WORK_ROOT / spec.case_id
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True, exist_ok=True)

    prepared = _prepare_case(spec, case_dir)
    program_path = prepared["program_path"]
    instance_path = prepared["instance_path"]
    target_path = prepared["target_path"]

    attempt_id = f"s1-attempt-{spec.case_id}"
    session_id = f"s1-session-{spec.case_id}"
    target_id = f"s1-target-{spec.case_id}"
    epoch = 1

    # -- trusted execution ------------------------------------------------
    observer = TrustedObserver(observer_key, case_dir / "execution")
    observation = observer.observe(
        program_path=program_path,
        input_path=instance_path,
        attempt_id=attempt_id,
        session_id=session_id,
        epoch=epoch,
        target_id=target_id,
    )
    obs_facts = observation["facts"]
    parsed_output = observation["parsed_output"]

    # -- producer authorship record ---------------------------------------
    producer_record = make_producer_record(
        producer_key, producer_priv,
        program_path=program_path,
        attempt_id=attempt_id,
        session_id=session_id,
        epoch=epoch,
        target_id=target_id,
    )

    # -- independent reference verdict ------------------------------------
    reference = ReferenceVerifier(reference_key)
    stdout_path = observation["stdout_path"]
    reference_out = reference.evaluate(
        target_state_path=target_path,
        stdout_path=stdout_path,
        attempt_id=attempt_id,
        epoch=epoch,
        target_id=target_id,
        session_id=session_id,
    )

    # -- write the evidence files ----------------------------------------
    write_json(case_dir / "artifact_record.json", producer_record)
    write_json(case_dir / "observation.json", observation["record"])
    write_json(case_dir / "reference_verdict.json", reference_out["record"])

    run_block = {
        "target_id": target_id,
        "attempt_id": attempt_id,
        "session_id": session_id,
        "epoch": epoch,
        "input_sha256": sha256_file(instance_path),
        "target_state_sha256": sha256_file(target_path),
        "program_source_sha256": sha256_file(program_path),
    }
    entries = _bundle_entries(case_dir)
    bundle_path = _write_bundle(case_dir, run_block, entries)
    bundle = read_json(bundle_path)

    # -- apply the preregistered mutation --------------------------------
    mutation = spec.mutation
    mutation_log: list[str] = []
    if mutation.startswith("drop_kind:"):
        kind = mutation.split(":", 1)[1]
        entry = _entry(bundle, kind)
        _drop_entry(bundle, kind)
        if entry is not None:
            target = case_dir / entry["path"]
            if target.exists():
                target.unlink()
        mutation_log.append(f"dropped evidence kind {kind}")
    elif mutation.startswith("delete_file:"):
        kind = mutation.split(":", 1)[1]
        entry = _entry(bundle, kind)
        if entry is not None:
            (case_dir / entry["path"]).unlink(missing_ok=True)
        mutation_log.append(f"deleted file for kind {kind}")
    elif mutation == "producer_digest_mismatch":
        record = read_json(case_dir / "artifact_record.json")
        facts = dict(record["payload"]["facts"])
        facts["program_sha256"] = sha256_bytes(b"not-the-program")
        payload = dict(record["payload"])
        payload["facts"] = facts
        unsigned = _unsigned_of(record)
        unsigned["payload"] = payload
        unsigned["signature_hex"] = _sign_raw(producer_priv, unsigned)
        write_json(case_dir / "artifact_record.json", unsigned)
        _refresh_entry_digest(bundle, case_dir, KIND_ARTIFACT_RECORD)
        mutation_log.append("producer re-signed a wrong program digest")
    elif mutation == "swap_program":
        fixture, instance = _fixture_for(spec)
        alt_source = _inventory_dir(spec) / "alt_candidate.py"
        if not alt_source.is_file():
            raise FileNotFoundError(
                f"frozen case inventory lacks alt_candidate.py for {spec.case_id}"
            )
        alt_path = case_dir / "program" / "candidate.py"
        alt_path.write_bytes(alt_source.read_bytes())
        _refresh_entry_digest(bundle, case_dir, KIND_PROGRAM_SOURCE)
        record = make_producer_record(
            producer_key, producer_priv,
            program_path=alt_path,
            attempt_id=attempt_id,
            session_id=session_id,
            epoch=epoch,
            target_id=target_id,
        )
        write_json(case_dir / "artifact_record.json", record)
        _refresh_entry_digest(bundle, case_dir, KIND_ARTIFACT_RECORD)
        mutation_log.append("credited program replaced by a different program")
    elif mutation == "swap_output":
        # Produce a *cryptographically valid* candidate that the observed
        # execution never produced, in a scratch directory, then present it.
        fixture, instance = _fixture_for(spec)
        scratch = case_dir / "scratch"
        scratch.mkdir(parents=True, exist_ok=True)
        scratch_program = scratch / "candidate.py"
        alt_correct = _inventory_dir(spec) / "alt_correct_candidate.py"
        if not alt_correct.is_file():
            raise FileNotFoundError(
                f"frozen case inventory lacks alt_correct_candidate.py for {spec.case_id}"
            )
        scratch_program.write_bytes(alt_correct.read_bytes())
        scratch_instance = scratch / "public_instance.json"
        write_json(scratch_instance, instance)
        scratch_observer = TrustedObserver(observer_key, scratch)
        scratch_obs = scratch_observer.observe(
            program_path=scratch_program,
            input_path=scratch_instance,
            attempt_id=attempt_id,
            session_id=session_id,
            epoch=epoch,
            target_id=target_id,
        )
        # The presented output file is the scratch output; the presented
        # stdout is replaced too, and the reference verdict is recomputed
        # over the scratch stdout.
        presented_output = case_dir / "execution" / "candidate_output.json"
        if scratch_obs["output_path"] is not None:
            shutil.copyfile(scratch_obs["output_path"], presented_output)
        presented_stdout = case_dir / "execution" / "executor_stdout.txt"
        shutil.copyfile(scratch_obs["stdout_path"], presented_stdout)
        _refresh_entry_digest(bundle, case_dir, KIND_PROGRAM_OUTPUT)
        _refresh_entry_digest(bundle, case_dir, KIND_EXECUTION_STDOUT)
        fresh = reference.evaluate(
            target_state_path=target_path,
            stdout_path=scratch_obs["stdout_path"],
            attempt_id=attempt_id,
            epoch=epoch,
            target_id=target_id,
            session_id=session_id,
        )
        write_json(case_dir / "reference_verdict.json", fresh["record"])
        _refresh_entry_digest(bundle, case_dir, KIND_REFERENCE_VERDICT)
        mutation_log.append("submitted output and reference verdict replaced with a valid candidate from another run")
    elif mutation == "reference_attempt_conflict":
        other = reference.evaluate(
            target_state_path=target_path,
            stdout_path=stdout_path,
            attempt_id=f"{attempt_id}-other",
            epoch=epoch,
            target_id=target_id,
            session_id=session_id,
        )
        write_json(case_dir / "reference_verdict.json", other["record"])
        _refresh_entry_digest(bundle, case_dir, KIND_REFERENCE_VERDICT)
        mutation_log.append("reference verdict bound to a different attempt")
    elif mutation == "reference_target_mismatch":
        alt_target = case_dir / "private" / "target_state.alt.json"
        alt_target.parent.mkdir(parents=True, exist_ok=True)
        alt_target.write_text(json.dumps(read_json(target_path), indent=1, sort_keys=False))
        other = reference.evaluate(
            target_state_path=alt_target,
            stdout_path=stdout_path,
            attempt_id=attempt_id,
            epoch=epoch,
            target_id=target_id,
            session_id=session_id,
        )
        write_json(case_dir / "reference_verdict.json", other["record"])
        _refresh_entry_digest(bundle, case_dir, KIND_REFERENCE_VERDICT)
        mutation_log.append("reference verdict computed against a different target state file")
    elif mutation == "observation_epoch_mismatch":
        record = read_json(case_dir / "observation.json")
        forged = resign_observation(record, observer_priv, epoch=epoch + 1)
        write_json(case_dir / "observation.json", forged)
        _refresh_entry_digest(bundle, case_dir, KIND_EXECUTION_OBSERVATION)
        mutation_log.append("observation signed under a stale epoch")
    elif mutation == "observation_attempt_mismatch":
        record = read_json(case_dir / "observation.json")
        forged = resign_observation(record, observer_priv, attempt_id=f"{attempt_id}-prior")
        write_json(case_dir / "observation.json", forged)
        _refresh_entry_digest(bundle, case_dir, KIND_EXECUTION_OBSERVATION)
        mutation_log.append("observation signed under a prior attempt")
    elif mutation == "prior_attempt_observation":
        prior = observer.observe(
            program_path=program_path,
            input_path=instance_path,
            attempt_id=f"{attempt_id}-prior",
            session_id=session_id,
            epoch=epoch - 1,
            target_id=target_id,
        )
        write_json(case_dir / "observation.json", prior["record"])
        _refresh_entry_digest(bundle, case_dir, KIND_EXECUTION_OBSERVATION)
        mutation_log.append("a prior attempt's real observation replayed into this attempt")
    elif mutation == "tamper_observation_signature":
        record = read_json(case_dir / "observation.json")
        sig = record["signature_hex"]
        flipped = ("0" if sig[0] != "0" else "1") + sig[1:]
        record["signature_hex"] = flipped
        write_json(case_dir / "observation.json", record)
        _refresh_entry_digest(bundle, case_dir, KIND_EXECUTION_OBSERVATION)
        mutation_log.append("observation signature tampered")
    elif mutation == "forge_observation_role":
        record = read_json(case_dir / "observation.json")
        forged = forge_observation_with_producer_key(record, producer_key, producer_priv)
        write_json(case_dir / "observation.json", forged)
        _refresh_entry_digest(bundle, case_dir, KIND_EXECUTION_OBSERVATION)
        mutation_log.append("observer record re-signed with the producer key")
    elif mutation == "duplicate_observation_entry":
        second = observer.observe(
            program_path=program_path,
            input_path=instance_path,
            attempt_id=attempt_id,
            session_id=session_id,
            epoch=epoch,
            target_id=target_id,
        )
        second_path = case_dir / "observation.second.json"
        write_json(second_path, second["record"])
        bundle["entries"].append({
            "kind": KIND_EXECUTION_OBSERVATION,
            "path": "observation.second.json",
            "sha256": sha256_file(second_path),
        })
        mutation_log.append("a second, different observation record added")
    elif mutation == "mutate_output_after_bundle":
        out = case_dir / "execution" / "candidate_output.json"
        out.write_text(out.read_text() + "\n")
        mutation_log.append("output artifact mutated after the bundle index was written")
    elif mutation in ("replay_shared_ledger", ""):
        mutation_log.append("no bundle mutation; replay handled as a second evaluation")
    else:  # pragma: no cover - defensive
        raise ValueError(f"unknown mutation {mutation!r}")

    write_json(bundle_path, bundle)

    # -- evaluation --------------------------------------------------------
    expectation = RunExpectation(
        target_id=target_id,
        attempt_id=attempt_id,
        epoch=epoch,
        session_id=session_id,
        input_sha256=run_block["input_sha256"],
        target_state_sha256=run_block["target_state_sha256"],
        program_source_sha256=run_block["program_source_sha256"],
    )

    decisions: dict[str, Any] = {}
    for name, cls in BASELINE_EVALUATORS.items():
        ev = cls(trust["public_bundle_path"], expectation, replay_state=ReplayState(max_uses=1))
        decisions[name] = ev.evaluate(bundle_path).as_dict()
    ev3 = AttributionEvaluator(trust["public_bundle_path"], expectation,
                                replay_state=ReplayState(max_uses=1), strict_execution=True)
    decisions["full"] = ev3.evaluate(bundle_path).as_dict()
    ev3_lenient = AttributionEvaluator(trust["public_bundle_path"], expectation,
                                       replay_state=ReplayState(max_uses=1), strict_execution=False)
    decisions["full_lenient"] = ev3_lenient.evaluate(bundle_path).as_dict()

    if mutation == "replay_shared_ledger":
        shared = ReplayState(max_uses=1)
        first = AttributionEvaluator(trust["public_bundle_path"], expectation,
                                     replay_state=shared, strict_execution=True)
        first.evaluate(bundle_path)
        second = AttributionEvaluator(trust["public_bundle_path"], expectation,
                                      replay_state=shared, strict_execution=True)
        decisions["full"] = second.evaluate(bundle_path).as_dict()
        # The preregistered case table declares R01 REJECT under BOTH the
        # strict and the lenient contract, so the lenient variant must consume
        # the same consumed replay slot.  (Exploratory deviation D-01: the
        # first implementation wired only the strict variant; see
        # s1_deviations.md.)
        shared_l = ReplayState(max_uses=1)
        first_l = AttributionEvaluator(trust["public_bundle_path"], expectation,
                                       replay_state=shared_l, strict_execution=False)
        first_l.evaluate(bundle_path)
        second_l = AttributionEvaluator(trust["public_bundle_path"], expectation,
                                        replay_state=shared_l, strict_execution=False)
        decisions["full_lenient"] = second_l.evaluate(bundle_path).as_dict()
        for name, cls in BASELINE_EVALUATORS.items():
            shared_b = ReplayState(max_uses=1)
            b1 = cls(trust["public_bundle_path"], expectation, replay_state=shared_b)
            b1.evaluate(bundle_path)
            b2 = cls(trust["public_bundle_path"], expectation, replay_state=shared_b)
            decisions[name] = b2.evaluate(bundle_path).as_dict()

    # -- frozen Stage01 pair (only where a direct analogue exists) ---------
    stage01: dict[str, Any] = {"applicable": spec.stage01_analogue == "yes"}
    if spec.stage01_analogue == "yes":
        exec_status = historical_execution_status(
            obs_facts.get("returncode"), bool(obs_facts.get("output_parsed"))
        )
        target_status = historical_target_status(exec_status, spec.condition, parsed_output)
        seed_int = int(sha256_bytes(spec.seed.encode())[:8], 16)
        credited = program_path
        if mutation == "swap_program":
            credited = program_path  # already replaced on disk
        stage01_dir = case_dir / "stage01"
        stage01_dir.mkdir(parents=True, exist_ok=True)
        # NOTE: ``build_stage01_certificate`` appends its own "stage01"
        # component, so it is handed ``case_dir`` (not ``stage01_dir``) and the
        # evidence files land in ``case_dir/stage01/`` -- the same directory the
        # Stage01-specific mutations below delete from.
        _cert, cert_path, public_path = build_stage01_certificate(
            case_dir,
            session_id=session_id,
            base_id=f"base-{spec.seed}",
            task=f"task-{spec.case_id}",
            condition=spec.condition,
            seed=seed_int,
            program_path=credited,
            target_status=target_status,
        )
        if mutation == "producer_digest_mismatch":
            cert = read_json(cert_path)
            cert["agent_artifact"]["sha256"] = sha256_bytes(b"not-the-program")
            write_json(cert_path, cert)
            public = read_json(public_path)
            public["agent_artifact"]["sha256"] = sha256_bytes(b"not-the-program")
            write_json(public_path, public)
        if mutation == "drop_kind:execution_observation":
            trace = stage01_dir / "execution_trace.json"
            trace.unlink(missing_ok=True)
        if mutation == "delete_file:program_source":
            (stage01_dir / "agent_artifact.json").unlink(missing_ok=True)
        candidate_path = case_dir / "execution" / "candidate_output.json"
        if not candidate_path.exists():
            stage01.update({
                "reference_verdict": "ERROR_NO_CANDIDATE_ARTIFACT",
                "validator_decision": "REJECT",
                "stage01_final_decision": "REJECTED",
                "note": "the historical path produces no candidate artifact for this execution status",
            })
        else:
            pair = run_frozen_stage01_pair(cert_path, public_path, target_path, candidate_path)
            stage01.update(pair)
        stage01["historical_execution_status"] = exec_status
        stage01["historical_target_status"] = target_status

    result = {
        "case_id": spec.case_id,
        "family": spec.family,
        "program": spec.program,
        "primitive": spec.primitive,
        "condition": spec.condition,
        "mutation": mutation,
        "mutation_log": mutation_log,
        "expected": {
            "decision": spec.expected_decision,
            "decision_lenient": spec.expected_decision_lenient,
            "crypto_success": spec.expected_crypto_success,
            "stage01_analogue": spec.stage01_analogue,
        },
        "observed": {
            "historical_execution_status": obs_facts.get("status"),
            "returncode": obs_facts.get("returncode"),
            "output_parsed": obs_facts.get("output_parsed"),
            "source_policy": obs_facts.get("source_policy"),
            "reference_verdict": reference_out["verdict"],
            "cryptographic_predicate": reference_out["facts"].get("cryptographic_predicate"),
            "decisions": {k: v["decision"] for k, v in decisions.items()},
            "reasons": {k: v.get("reasons", []) for k, v in decisions.items()},
            "levels": {k: v.get("levels", {}) for k, v in decisions.items()},
        },
        "stage01": stage01,
        "bundle_path": str(bundle_path.relative_to(STAGE1_ROOT)),
        "decisions_detail": decisions,
    }
    return result


def main() -> int:
    # ---- fail-closed integrity preflight (audited remediation component) ----
    # The confirmatory run refuses to start unless the frozen manifest verifies
    # against the *unmodified* vetted verifier.
    from manifest_verifier import PreflightError, preflight_then_execute

    if not INTEGRITY_MANIFEST.is_file():
        raise PreflightError(
            f"no integrity manifest at {INTEGRITY_MANIFEST}; run s1_freeze.py first"
        )

    def _execute() -> int:
        custody = setup_trust(force=False)
        from s1_common import load_ed25519_private_key

        key_paths = {
            role: STAGE1_ROOT / info["private_key_path"]
            for role, info in custody["roles"].items()
        }
        trust = {
            "public_bundle_path": STAGE1_ROOT / custody["public_bundle"],
            "key_paths": key_paths,
            "custody": custody,
        }
        observer_key = key_paths["execution_observer"]
        producer_key = key_paths["artifact_producer"]
        reference_key = key_paths["reference_verifier"]
        observer_priv = load_ed25519_private_key(observer_key)
        producer_priv = load_ed25519_private_key(producer_key)

        RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
        results = []
        for spec in CASE_SPECS:
            print(f"[stage1] case {spec.case_id} ...", flush=True)
            results.append(
                run_case(spec, trust, observer_key, observer_priv, producer_key, producer_priv,
                         reference_key)
            )
        out = RESULTS_ROOT / "results.json"
        write_json(out, {
            "schema": "acts-next-phase/s1-results/1",
            "case_count": len(results),
            "evaluator_names": list(EVALUATOR_NAMES),
            "results": results,
        })
        print(f"[stage1] wrote {out}")
        return 0

    return preflight_then_execute(INTEGRITY_MANIFEST, s1_common.REPO_ROOT, _execute)


if __name__ == "__main__":
    raise SystemExit(main())
