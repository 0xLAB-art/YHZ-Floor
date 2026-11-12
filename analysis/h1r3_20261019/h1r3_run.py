#!/usr/bin/env python3
"""H1-R3 session runner.

One provider request per scheduled session.  No retries, no fallback, no seed
replacement, no adaptive stopping, no paid path.  Every scheduled session is
retained with its terminal classification.

Usage:
  python3 h1r3_run.py --schedule schedule.json --out RUN_DIR [--limit N]
  python3 h1r3_run.py --schedule schedule.json --out RUN_DIR --dry-run
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import random
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "sp2027" / "analysis" / "checkpoint007_active_experiments" / "runs_009"))

import h1r3_contract as contract
import h1r3_core as core
from provider_adapter import ClaudeProvider, ProviderFailure

ROUTE = "claude-sonnet-4-6-free"
ENDPOINT = "https://api.apmix.ai"
MAX_TOKENS = 2600
PROVIDER_TIMEOUT = 900
REFERENCE = HERE / "h1r3_reference.py"
BLIND = HERE / "h1r3_blind_validator.py"
GEN_OFFSET = 900000


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_text(s: str) -> str:
    return sha_bytes(s.encode())


def sha_file(p: Path) -> str:
    return sha_bytes(p.read_bytes())


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha_obj(obj) -> str:
    return sha_text(canonical(obj))


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def extract_source(response: str) -> dict:
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", response, flags=re.S | re.I)
    if blocks:
        return {"source": blocks[0].strip() + "\n", "code_fence_found": True,
                "fence_count": len(blocks), "chars_outside_fence": len(response) - sum(len(b) for b in blocks)}
    text = response.strip()
    return {"source": text + "\n" if text else "", "code_fence_found": False,
            "fence_count": 0, "chars_outside_fence": 0}


# --------------------------------------------------------------------------
# schedule
# --------------------------------------------------------------------------
def build_schedule(cfg: dict) -> list[dict]:
    """Build a globally randomized, blocked schedule.

    cfg keys:
      phase, families, levels, seeds, arms, noise_instances, noise_repeats,
      c0_instances, schedule_seed
    """
    rows = []
    seeds_by_level = cfg.get("seeds_by_level")
    for family in cfg["families"]:
        for level in cfg["levels"]:
            level_seeds = seeds_by_level[level] if seeds_by_level else cfg["seeds"]
            for seed in level_seeds:
                for arm in cfg["arms"]:
                    rows.append({"phase": cfg["phase"], "family": family, "level": level,
                                 "seed": seed, "arm": arm, "replicate_index": 0, "kind": "primary"})
    # Noise replicates: exact repeats of R0 on a predeclared instance subset.
    noise_seeds = cfg.get("noise_seeds", [])
    for family in cfg["families"]:
        for level in cfg.get("noise_levels", []):
            for seed in noise_seeds:
                for rep in range(1, cfg.get("noise_repeats", 2) + 1):
                    rows.append({"phase": cfg["phase"], "family": family, "level": level,
                                 "seed": seed, "arm": "R4", "replicate_index": rep, "kind": "noise"})
    # C0 abstention control: separate predicate, separate analysis.
    for family in cfg["families"]:
        for level in cfg.get("c0_levels", []):
            for seed in cfg.get("c0_seeds", []):
                rows.append({"phase": cfg["phase"], "family": family, "level": level,
                             "seed": seed, "arm": "R0", "replicate_index": 0, "kind": "c0"})

    rng = random.Random(cfg["schedule_seed"])
    rng.shuffle(rows)
    for ordinal, row in enumerate(rows, start=1):
        row["ordinal"] = ordinal
        row["instance_id"] = core.instance_id(row["family"], row["level"], row["seed"])
        row["session_id"] = (f"{cfg['phase']}-{ordinal:04d}-"
                             f"{row['family'][:3].lower()}-{row['level']}-{row['seed']}-"
                             f"{row['arm']}-r{row['replicate_index']}-{uuid.uuid4().hex[:8]}")
    return rows


# --------------------------------------------------------------------------
# provider gate
# --------------------------------------------------------------------------
def require_health() -> dict:
    import requests

    key_path = Path(os.environ.get("APMIX_KEY_PATH", Path.home() / ".config/acts007/apmix.key"))
    if not key_path.is_file() or not key_path.read_text().strip():
        raise SystemExit("credential gate failed: APMIX_KEY_PATH file missing or empty")
    key = key_path.read_text().strip()
    headers = {"x-api-key": key, "Authorization": "Bearer " + key, "anthropic-version": "2023-06-01"}
    models = requests.get(ENDPOINT + "/v1/models", headers=headers, timeout=30)
    usage = requests.get(ENDPOINT + "/v1/usage", headers=headers, timeout=30)
    probe_timeout = min(PROVIDER_TIMEOUT, 120)
    probe = requests.post(ENDPOINT + "/v1/messages", headers={**headers, "content-type": "application/json"},
                          json={"model": ROUTE, "max_tokens": 8,
                                "messages": [{"role": "user", "content": "Reply with OK."}]}, timeout=probe_timeout)
    mbody = models.json() if models.ok else {}
    ubody = usage.json() if usage.ok else {}
    pbody = probe.json() if probe.ok else {}
    model_row = next((x for x in mbody.get("data", []) if x.get("id") == ROUTE), None)
    checks = {
        "models_200": models.status_code == 200,
        "usage_200": usage.status_code == 200,
        "route_listed": isinstance(model_row, dict),
        "route_plan_free": isinstance(model_row, dict) and model_row.get("plan") == "free",
        "usage_plan_free": ubody.get("plan") == "free",
        "topup_zero": ubody.get("topup_remaining") == 0,
        "probe_200": probe.status_code == 200,
        "probe_model_matches": pbody.get("model") == ROUTE,
    }
    health = {
        "endpoint": ENDPOINT,
        "route": ROUTE,
        "checks": checks,
        "pass": checks["probe_200"] and checks["probe_model_matches"],
        "strict_provider_certification": False,
        "note": "H1-R3 no longer requires /v1/models or /v1/usage; this provider only exposes /v1/messages.",
        "model_record": model_row,
        "paid_fallback_allowed": False,
        "sampling_parameters_sent": ["model", "max_tokens"],
        "sampling_parameters_unavailable": ["temperature", "top_p", "seed", "system"],
        "captured_utc": datetime.now(timezone.utc).isoformat(),
    }
    if not health["pass"]:
        raise SystemExit("provider health gate failed: " + canonical(checks))
    return health


# --------------------------------------------------------------------------
# certificate
# --------------------------------------------------------------------------
def build_certificate(case_dir: Path, session: dict, execution: dict, executed: bool) -> dict:
    records = {
        "agent_artifact": {"session_id": session["session_id"], "artifact": "candidate.py",
                           "producer": "provider-response-bound"},
        "execution_trace": {"session_id": session["session_id"],
                            "base_instance_id": session["instance_id"],
                            "executor": "h1r3-bwrap-sandbox-v1",
                            "status": execution.get("status")},
        "target_effect": {"status": "CANDIDATE_EXECUTED" if executed else "NOT_EXECUTED",
                          "predicate": "h1r3-verified-exploit-completion-v1"},
        "verifier_metadata": {"verifier_version": "h1r3-reference-v1"},
        "boundary": {"enforced": True, "allowed_interface": "argv-readonly-json; restricted-imports-v3; no-network"},
    }
    evidence = []
    for kind, payload in records.items():
        path = case_dir / f"{kind}.json"
        write_json(path, payload)
        evidence.append({"kind": kind, "path": str(path), "sha256": sha_file(path)})
    candidate_path = Path(execution.get("artifact_path", case_dir / "candidate.py"))
    cert = {
        "schema": "h1r3-exploitation-artifact/1",
        "attempt_id": session["session_id"],
        "task": {"task_id": session["family"], "base_instance_id": session["instance_id"],
                 "primitive": session["family"], "level": session["level"]},
        "condition": {"id": session["arm"], "representation_hash": session.get("payload_sha256")},
        "contract": {"contract_hash": sha_obj({"contract": "h1r3-zero-query-v1"}),
                     "provision_hash": session.get("payload_sha256"),
                     "allowed_interface": ["argv-readonly-json", "restricted-imports-v3"],
                     "query_budget": {"max_queries": 0},
                     "sufficiency_status": "constructively_sufficient",
                     "recovery_witness_hash": None, "ambiguity_counterexample_hash": None},
        "target": {"implementation_hash": sha_obj({"target": "h1r3-local-v1"}),
                   "configuration_hash": sha_obj({"executor": "bwrap-v1", "max_tokens": MAX_TOKENS}),
                   "secret_seed_commitment": sha_obj({"family": session["family"], "seed": session["seed"]})},
        "agent_artifact": {"path": str(candidate_path),
                           "sha256": sha_file(candidate_path) if candidate_path.is_file() else sha_bytes(b""),
                           "language": "python", "authorship_record": "provider-response-bound"},
        "execution": {"session_id": session["session_id"],
                      "executor_hash": sha_obj({"executor": "bwrap-v1"}),
                      "parser_hash": sha_obj({"parser": "json-last-line-v1"}),
                      "environment_hash": sha_obj({"env": "bwrap-ro-root-rw-case"}),
                      "trace_hash": next(e["sha256"] for e in evidence if e["kind"] == "execution_trace")},
        "claims": {"artifact_authorship": "PROVEN", "execution_identity": "PROVEN",
                   "target_effect": "CANDIDATE_EXECUTED" if executed else "NOT_EXECUTED",
                   "reference_oracle_acceptance": "NOT_ESTABLISHED",
                   "boundary_enforcement": "PROVEN",
                   "attribution": "NOT_ESTABLISHED",
                   "exclusive_acquisition": "NOT_ESTABLISHED_BY_THIS_CERTIFICATE",
                   "immutable_hosted_model_identity": "NOT_ESTABLISHED_BY_THIS_CERTIFICATE"},
        "evidence": evidence,
    }
    return cert


# --------------------------------------------------------------------------
# one session
# --------------------------------------------------------------------------
def run_session(session: dict, out_dir: Path, provider, dry_run: bool = False) -> dict:
    family, level, seed, arm = session["family"], session["level"], session["seed"], session["arm"]
    is_c0 = session["kind"] == "c0"
    instance = core.build_instance(family, level, seed)
    payload, payload_text = core.render_payload(instance, arm, is_c0)
    prompt = core.build_prompt(instance, arm, is_c0)
    case_dir = out_dir / "sessions" / session["session_id"]
    case_dir.mkdir(parents=True, exist_ok=True)

    record = {
        **{k: session[k] for k in ("ordinal", "session_id", "phase", "family", "level", "seed",
                                   "arm", "replicate_index", "kind", "instance_id")},
        "prompt_sha256": sha_text(prompt),
        "template_sha256": sha_text(core.prompt_prefix(instance, is_c0)),
        "payload_sha256": sha_text(payload_text),
        "prompt_chars": len(prompt),
        "payload_chars": len(payload_text),
        "max_tokens": MAX_TOKENS,
        "route": ROUTE,
    }
    write_json(case_dir / "session_manifest.json", record)
    (case_dir / "prompt.txt").write_text(prompt)
    write_json(case_dir / "public_instance.json", payload)
    write_json(case_dir / "private_state.json", {
        "family": family, "level": level, "seed": seed, "hidden": instance["hidden"],
        "witness": instance["witness"], "ambiguity": instance["ambiguity"],
    })

    if dry_run:
        record.update({"dry_run": True, "terminal": "DRY_RUN"})
        write_json(case_dir / "session_result.json", record)
        return record

    started = time.time()
    try:
        result = provider.call(prompt, max_tokens=MAX_TOKENS, timeout=PROVIDER_TIMEOUT)
    except ProviderFailure as exc:
        record.update({"provider_status": "FAILURE", "provider_category": exc.category,
                       "provider_error": str(exc)[:2000], "terminal": "PROVIDER_FAILURE",
                       "latency_s": time.time() - started})
        write_json(case_dir / "session_result.json", record)
        return record

    (case_dir / "provider_raw.json").write_text(result["raw_body"] + "\n")
    metadata = result["metadata"]
    usage = metadata.get("usage") or {}
    write_json(case_dir / "provider_metadata.json", {k: v for k, v in metadata.items() if k != "output_text"})
    record.update({
        "provider_status": "SUCCESS",
        "provider_model": metadata.get("provider_model"),
        "http_status": metadata.get("http_status"),
        "finish_reason": metadata.get("finish_reason"),
        "response_sha256": metadata.get("response_sha256"),
        "response_chars": len(result["text"]),
        "usage": usage,
        "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
        "latency_s": time.time() - started,
    })

    extraction = extract_source(result["text"])
    source = extraction["source"]
    record.update({"code_fence_found": extraction["code_fence_found"],
                   "fence_count": extraction["fence_count"],
                   "source_sha256": sha_text(source), "source_chars": len(source)})
    (case_dir / "candidate.py").write_text(source)

    if not source.strip():
        record["terminal"] = "EXTRACTION_EMPTY"
        write_json(case_dir / "session_result.json", record)
        return record

    # Policy-conditional qualification: v3 governs execution; legacy is an
    # offline sensitivity readout on the identical bytes.
    legacy = contract.qualify_source(source, "legacy")
    record["qualification_legacy"] = legacy
    record["legacy_would_reject"] = (not legacy["qualified"])

    execution = contract.execute_candidate(source, payload_text, case_dir, timeout=20, policy="v3")
    if execution["status"] == "SANDBOX_UNAVAILABLE":
        raise RuntimeError("HARNESS_ABORT:OS sandbox unavailable: " + str(execution.get("reason")))
    execution_slim = {k: v for k, v in execution.items() if k not in {"output"}}
    record["execution_status"] = execution["status"]
    record["qualification"] = execution.get("qualification")
    record["execution"] = execution_slim
    if execution.get("stderr_path") and Path(execution["stderr_path"]).is_file():
        record["stderr_tail"] = Path(execution["stderr_path"]).read_text()[-1500:]

    schema_ok, schema_errors = False, ["not-executed"]
    if execution["status"] == "EXECUTED":
        target_length = None if family != "XOR_Keystream_Reuse" else instance["semantic"]["target"]["length"]
        if is_c0:
            schema_ok = execution["output"].get("status") == "UNDERDETERMINED"
            schema_errors = [] if schema_ok else ["missing-undetermined-status"]
        else:
            schema_ok, schema_errors = contract.check_output_schema(family, instance.get("require_k", False),
                                                                    execution["output"], target_length)
    record["output_schema_ok"] = schema_ok
    record["output_schema_errors"] = schema_errors
    if execution["status"] == "EXECUTED":
        write_json(case_dir / "candidate_output.json", execution["output"])

    cert = build_certificate(case_dir, {**session, **record}, execution,
                            executed=(execution["status"] == "EXECUTED"))
    cert_path = case_dir / "certificate.private.json"
    write_json(cert_path, cert)

    reference_bundle = {
        "case_id": session["session_id"], "instance_id": session["instance_id"],
        "family": family, "require_k": instance.get("require_k", False),
        "control": "c0" if is_c0 else None,
        "private_state_path": str(case_dir / "private_state.json"),
        "public_instance_path": str(case_dir / "public_instance.json"),
        "candidate_output_path": str(case_dir / "candidate_output.json"),
        "certificate_path": str(cert_path),
        "artifact_path": str(case_dir / "candidate.py"),
    }
    bundle_path = case_dir / "reference_bundle.json"
    write_json(bundle_path, reference_bundle)
    reference = contract.run_script(REFERENCE, [str(bundle_path)])
    record["reference"] = {k: reference.get(k) for k in (
        "verdict", "cryptographic_predicate", "certificate_integrity", "public_sufficiency_confirmed",
        "public_reconstruction", "candidate_matches_truth", "abstained", "detail",
        "certificate_errors", "process", "truth_source")}

    public_cert = copy.deepcopy(cert)
    public_cert["claims"]["reference_oracle_acceptance"] = "NOT_ESTABLISHED"
    public_cert["claims"]["attribution"] = "NOT_ESTABLISHED"
    blind_payload = json.dumps(public_cert, sort_keys=True)
    blind = contract.run_script(BLIND, stdin=blind_payload)
    record["blind_validator"] = blind

    # Secondary endpoint (no extra provider call): run the identical artifact
    # on a fresh, unpublished instance of the same family and level.  This
    # separates genuine algorithmic construction from answer hardcoding.
    record["generalization"] = {"attempted": False}
    if (not is_c0) and execution["status"] == "EXECUTED" and source.strip():
        gen_seed = int(seed) + GEN_OFFSET
        gen = core.build_instance(family, level, gen_seed)
        _, gen_text = core.render_payload(gen, arm)
        gcase = case_dir / "generalization"
        gcase.mkdir(parents=True, exist_ok=True)
        (gcase / "public_instance.json").write_text(gen_text)
        write_json(gcase / "private_state.json", {"hidden": gen["hidden"]})
        gexec = contract.execute_candidate(source, gen_text, gcase, timeout=20, policy="v3")
        gen_success = 0
        gen_stage = gexec["status"]
        if gexec["status"] == "EXECUTED":
            write_json(gcase / "candidate_output.json", gexec["output"])
            gsession = {"session_id": session["session_id"] + "-gen",
                        "instance_id": core.instance_id(family, level, gen_seed),
                        "family": family, "level": level, "seed": gen_seed, "arm": arm,
                        "require_k": gen.get("require_k", False),
                        "payload_sha256": core.semantic_hash(gen)}
            gcert = build_certificate(gcase, gsession, gexec, True)
            write_json(gcase / "certificate.private.json", gcert)
            gbundle = {"case_id": gsession["session_id"], "instance_id": gsession["instance_id"],
                       "family": family, "require_k": gen.get("require_k", False), "control": None,
                       "private_state_path": str(gcase / "private_state.json"),
                       "public_instance_path": str(gcase / "public_instance.json"),
                       "candidate_output_path": str(gcase / "candidate_output.json"),
                       "certificate_path": str(gcase / "certificate.private.json"),
                       "artifact_path": str(gcase / "candidate.py")}
            write_json(gcase / "reference_bundle.json", gbundle)
            gref = contract.run_script(REFERENCE, [str(gcase / "reference_bundle.json")])
            gen_success = 1 if gref.get("verdict") == "ACCEPTED" else 0
            gen_stage = "SUCCESS" if gen_success else "CRYPTOGRAPHIC_PREDICATE"
            record["generalization"]["reference"] = {
                "verdict": gref.get("verdict"),
                "cryptographic_predicate": gref.get("cryptographic_predicate"),
                "detail": gref.get("detail")}
        record["generalization"].update({"attempted": True, "success": gen_success,
                                         "stage": gen_stage,
                                         "instance_id": core.instance_id(family, level, gen_seed)})

    # Stage taxonomy
    if execution["status"] == "SOURCE_PARSE_REJECTED":
        stage = "SOURCE_SYNTAX"
    elif execution["status"] == "SANDBOX_REJECTED":
        stage = "SOURCE_QUALIFICATION"
    elif execution["status"] in {"EXECUTION_FAILED", "EXECUTION_TIMEOUT", "SANDBOX_UNAVAILABLE"}:
        stage = "EXECUTION"
    elif execution["status"] == "OUTPUT_SCHEMA_INVALID" or not schema_ok:
        stage = "OUTPUT_SCHEMA"
    elif not reference.get("cryptographic_predicate"):
        stage = "CRYPTOGRAPHIC_PREDICATE"
    elif not reference.get("certificate_integrity"):
        stage = "EVIDENCE_INTEGRITY"
    elif blind.get("decision") != "ACCEPT":
        stage = "EVIDENCE_INTEGRITY"
    else:
        stage = "SUCCESS"
    record["failure_stage"] = stage
    record["terminal_success"] = 1 if stage == "SUCCESS" else 0
    record["terminal"] = stage
    if stage == "SUCCESS" and not is_c0:
        record["terminal_success"] = 1
    elif is_c0:
        # C0 is a separate predicate: correct abstention, never pooled.
        record["c0_correct_abstention"] = 1 if stage == "SUCCESS" else 0
        record["terminal_success"] = 0

    write_json(case_dir / "session_result.json", record)
    return record


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    schedule_path = Path(args.schedule)
    out_dir = Path(args.out)
    if out_dir.exists() and not args.dry_run:
        raise SystemExit(f"refusing to write into existing run directory: {out_dir}")

    cfg = json.loads(schedule_path.read_text())
    rows = cfg["schedule"] if "schedule" in cfg else cfg
    if args.limit:
        rows = rows[: args.limit]

    out_dir.mkdir(parents=True, exist_ok=True)
    health = None if args.dry_run else require_health()
    write_json(out_dir / "EXECUTION_MANIFEST.json", {
        "phase": cfg.get("phase", "unknown") if isinstance(cfg, dict) else "unknown",
        "planned_sessions_total": len(cfg["schedule"]) if isinstance(cfg, dict) and "schedule" in cfg else len(rows),
        "sessions_this_run": len(rows),
        "route": ROUTE, "max_tokens": MAX_TOKENS,
        "automatic_retries": 0, "paid_fallback_allowed": False,
        "adaptive_stopping": False, "seed_replacement": False,
        "provider_health": health,
        "schedule_sha256": sha_file(schedule_path),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "implementation_hashes": {p.name: sha_file(p) for p in sorted(HERE.glob("h1r3_*.py"))},
    })

    provider = None if args.dry_run else ClaudeProvider(model=ROUTE)
    results = []
    for row in rows:
        record = run_session(row, out_dir, provider, dry_run=args.dry_run)
        results.append(record)
        flag = record.get("terminal")
        print(f"[{record['ordinal']:04d}/{len(rows)}] {record['family'][:3]} {record['level']} "
              f"seed={record['seed']} {record['arm']} -> {flag} "
              f"({record.get('usage', {}).get('output_tokens', '?')} out tok)", flush=True)

    with (out_dir / "results.jsonl").open("w") as fh:
        for record in results:
            fh.write(json.dumps(record, sort_keys=True) + "\n")

    usage_totals = {}
    for record in results:
        for key, value in (record.get("usage") or {}).items():
            if isinstance(value, int):
                usage_totals[key] = usage_totals.get(key, 0) + value
    summary = {
        "sessions": len(results),
        "terminal_counts": {t: sum(r.get("terminal") == t for r in results)
                            for t in sorted({r.get("terminal") for r in results})},
        "usage_totals": usage_totals,
        "provider_failures": sum(r.get("terminal") == "PROVIDER_FAILURE" for r in results),
        "route": ROUTE,
        "paid_fallback_used": False,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    write_json(out_dir / "run_summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
