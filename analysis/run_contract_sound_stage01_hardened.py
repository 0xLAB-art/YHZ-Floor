#!/usr/bin/env python3
"""Hardened deterministic Stage 0/1 verification pass.

No model/provider/network calls. Creates a new output directory and never
modifies the manuscript or protected result locks.
"""
from __future__ import annotations
import base64, copy, hashlib, json, random, subprocess, sys, time
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "sp2027" / "analysis" / "contract_sound_stage01_hardened_v2_20261018"
SCHEMA_PATH = ROOT / "sp2027" / "analysis" / "contract_sound_artifact_schema_v1.json"
VALIDATOR = HERE / "contract_sound_stage01_validator_v2.py"
REFERENCE = HERE / "contract_sound_stage01_reference_verifier_v2.py"
PROTOCOL_COMMIT = "4743d186bb64b07f5f81d5448bce3f2ab0237563"
PROTECTED = [ROOT / p for p in ["sp2027/analysis/RESULTS_LOCK.json", "sp2027/analysis/RESULTS_LOCK_H1PC.json", "sp2027/paper/main.tex", "sp2027/paper/main.pdf"]]
sys.path.insert(0, str(HERE))
import run_contract_sound_stage01 as base


def sha_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def sha_file(p: Path) -> str: return sha_bytes(p.read_bytes())
def canonical(o) -> bytes: return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()
def hobj(o) -> str: return sha_bytes(canonical(o))
def write_json(p: Path, o) -> None:
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(o, indent=2, sort_keys=True) + "\n")


def independent_decode(task: str, obj: dict) -> dict:
    if task == "ECDSA_Nonce_Reuse":
        def scalar(v): return f"{int.from_bytes(base64.b64decode(v), 'big'):064x}"
        if obj["encoding"] == "json-hex-v1":
            return {"primitive": task, "public_key": obj["public_key"], "signature_1": obj["signature_1"], "signature_2": obj.get("signature_2")}
        return {"primitive": task, "public_key": [scalar(x) for x in obj["public_key"]], "signature_1": {k: scalar(v) for k, v in obj["signature_1"].items()}, "signature_2": {k: scalar(v) for k, v in obj["signature_2"].items()} if obj.get("signature_2") else None}
    if obj["encoding"] == "json-hex-v1":
        return {"primitive": task, "ciphertext_1": obj["ciphertext_1"], "ciphertext_2": obj["ciphertext_2"], "known_plaintext_1": obj.get("known_plaintext_1")}
    return {"primitive": task, "ciphertext_1": base64.b64decode(obj["ciphertext_1"]).hex(), "ciphertext_2": base64.b64decode(obj["ciphertext_2"]).hex(), "known_plaintext_1": base64.b64decode(obj["known_plaintext_1"]).hex() if obj.get("known_plaintext_1") else None}


def public_cert(cert: dict) -> dict:
    out = copy.deepcopy(cert)
    out.pop("verification", None)
    out["claims"]["reference_oracle_acceptance"] = "NOT_ESTABLISHED"
    return out


def evidence(case: Path, session: str, base_id: str, status: str, *, boundary=True, version="stage01-reference-v1"):
    records = {
        "agent_artifact": {"session_id": session, "artifact": "candidate.json", "producer": "deterministic-stage01-hardened"},
        "execution_trace": {"session_id": session, "base_instance_id": base_id, "executor": "stage01-executor-v1"},
        "target_effect": {"status": status, "predicate": "task-specific-cryptographic-predicate-v1"},
        "verifier_metadata": {"verifier_version": version, "implementation": "independent-reference-v1"},
        "boundary": {"enforced": boundary, "allowed_interface": "contract-sound-v1"},
    }
    out = []
    for kind, obj in records.items():
        p = case / f"{kind}.json"; write_json(p, obj)
        out.append({"kind": kind, "path": str(p), "sha256": sha_file(p)})
    return out


def make_cert(case: Path, idx: int, task: str, seed: int, valid: bool) -> tuple[dict, Path, Path]:
    case.mkdir(parents=True, exist_ok=True)
    inst = base.make_ecdsa(seed) if task == "ECDSA_Nonce_Reuse" else base.make_chacha(seed)
    primitive = task
    if task == "ECDSA_Nonce_Reuse":
        target = {"primitive": primitive, **inst["semantic"]}
        candidate = {"d": f"{inst['hidden']['d']:064x}", "k": f"{inst['hidden']['k']:064x}"}
        if not valid: candidate["d"] = f"{(inst['hidden']['d'] ^ 1):064x}"
    else:
        target = {"primitive": primitive, **inst["semantic"]}
        candidate = {"plaintext_2": inst["witness"]["plaintext_2"]}
        if not valid: candidate["plaintext_2"] = (bytes.fromhex(candidate["plaintext_2"][:-2] + ("00" if candidate["plaintext_2"][-2:] != "00" else "01"))).hex()
    target_path = case / "target_state.private.json"; candidate_path = case / "candidate.json"
    write_json(target_path, target); write_json(candidate_path, candidate)
    session = f"stage01-hardened-session-{idx:03d}"; base_id = f"{task}-base-{seed:02d}"
    status = "OBSERVED" if valid else "NOT_OBSERVED"
    ev = evidence(case, session, base_id, status)
    cert = {
      "schema": "contract-sound-exploitation-artifact/1", "attempt_id": f"stage01-hardened-{idx:03d}",
      "task": {"task_id": f"stage01-{task}", "base_instance_id": base_id, "primitive": primitive},
      "condition": {"id": "C1", "representation_hash": hobj({"representation": "canonical", "seed": seed}), "order_seed": seed},
      "contract": {"contract_hash": hobj({"contract": "stage01-zero-query", "task": task}), "provision_hash": hobj({"provision": seed}), "allowed_interface": ["instance_file"], "query_budget": {"max_queries": 0, "max_query_bytes": 0, "max_query_time_ms": 0}, "sufficiency_status": "constructively_sufficient", "recovery_witness_hash": hobj(inst["witness"]), "ambiguity_counterexample_hash": None},
      "target": {"implementation_hash": hobj({"target": task, "version": "deterministic-v1"}), "configuration_hash": hobj({"config": "stage01-zero-query"}), "secret_seed_commitment": hobj({"task": task, "seed": seed})},
      "agent_artifact": {"path": str(candidate_path), "sha256": sha_file(candidate_path), "language": "json", "authorship_record": "deterministic-stage01"},
      "execution": {"session_id": session, "executor_hash": hobj({"executor": "v1"}), "parser_hash": hobj({"parser": "v1"}), "environment_hash": hobj({"env": "stage01-hardened"}), "trace_hash": ev[1]["sha256"]},
      "verification": {"raw_verdict": "ACCEPTED" if valid else "REJECTED", "reference_verdict": "ACCEPTED" if valid else "REJECTED", "validator_verdict": "PENDING", "target_effect": status, "validation_overhead_ms": None},
      "claims": {"artifact_authorship": "PROVEN", "execution_identity": "PROVEN", "target_effect": status, "reference_oracle_acceptance": "ACCEPTED" if valid else "REJECTED", "boundary_enforcement": "PROVEN", "attribution": "PROVEN" if valid else "NOT_ESTABLISHED", "exclusive_acquisition": "NOT_ESTABLISHED_BY_THIS_CERTIFICATE", "immutable_hosted_model_identity": "NOT_ESTABLISHED_BY_THIS_CERTIFICATE"},
      "evidence": ev,
    }
    cert_path = case / "certificate.private.json"; write_json(cert_path, cert)
    return cert, target_path, candidate_path


def mutate(cert: dict, case: Path, defect: str, variant: int) -> None:
    by = {x["kind"]: x for x in cert["evidence"]}
    if defect == "wrong_field":
        write_json(case / "target_effect.json", {"status": "NOT_OBSERVED", "predicate": "task-specific-cryptographic-predicate-v1"})
    elif defect == "stale_binding":
        write_json(case / "execution_trace.json", {"session_id": cert["execution"]["session_id"], "base_instance_id": "stale-base", "executor": "stage01-executor-v1"})
    elif defect == "replay_cross_session":
        write_json(case / "execution_trace.json", {"session_id": "other-session", "base_instance_id": cert["task"]["base_instance_id"], "executor": "stage01-executor-v1"})
    elif defect == "verifier_version_mismatch":
        write_json(case / "verifier_metadata.json", {"verifier_version": "stage01-reference-v0", "implementation": "independent-reference-v1"})
    elif defect == "interface_contamination":
        write_json(case / "boundary.json", {"enforced": False, "allowed_interface": "contract-sound-v1+hidden-channel"})
    for item in cert["evidence"]:
        p = Path(item["path"]); item["sha256"] = sha_file(p)
    # Wrong-field and stale/replay defects intentionally keep the certificate's
    # declared bindings stale; all other mutations require updated file hashes.
    if defect in {"wrong_field", "stale_binding", "replay_cross_session", "verifier_version_mismatch", "interface_contamination"}:
        if defect == "wrong_field":
            # Evidence bytes changed but advertised hash remains the old digest.
            item = by["target_effect"]; item["sha256"] = hobj({"stale": "wrong-field", "variant": variant})
        elif defect in {"stale_binding", "replay_cross_session"}:
            item = by["execution_trace"]; item["sha256"] = hobj({"stale": defect, "variant": variant})
        # version/boundary mutations are semantically invalid even with honest hashes.


def invoke(path: Path, arg: Path | None = None, data: dict | None = None) -> tuple[dict, float]:
    cmd = [sys.executable, str(path)] + ([str(arg)] if arg else [])
    start = time.perf_counter(); p = subprocess.run(cmd, input=json.dumps(data) if data is not None else None, text=True, capture_output=True, check=False); elapsed = (time.perf_counter() - start) * 1000
    if p.returncode != 0: raise RuntimeError(f"{path}: {p.stderr}")
    return json.loads(p.stdout), elapsed


def runtime_integrity(cert: dict) -> bool:
    try:
        by_kind = {item["kind"]: item for item in cert["evidence"]}
        required = {"agent_artifact", "execution_trace", "target_effect", "verifier_metadata", "boundary"}
        if not required.issubset(by_kind): return False
        for item in cert["evidence"]:
            p = Path(item["path"])
            if not p.is_file() or sha_file(p) != item["sha256"]: return False
        trace = json.loads(Path(by_kind["execution_trace"]["path"]).read_text())
        metadata = json.loads(Path(by_kind["verifier_metadata"]["path"]).read_text())
        effect = json.loads(Path(by_kind["target_effect"]["path"]).read_text())
        boundary = json.loads(Path(by_kind["boundary"]["path"]).read_text())
        return (trace.get("session_id") == cert["execution"]["session_id"] and
                trace.get("base_instance_id") == cert["task"]["base_instance_id"] and
                metadata.get("verifier_version") == "stage01-reference-v1" and
                effect.get("status") == cert["claims"]["target_effect"] and
                boundary.get("enforced") is True and
                cert["claims"].get("boundary_enforcement") == "PROVEN")
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError):
        return False


def paired_analysis() -> dict:
    outcomes = [(1, 1), (1, 0), (0, 1), (1, 1)] * 6
    n = len(outcomes); c1 = sum(x for x, _ in outcomes) / n; c2 = sum(y for _, y in outcomes) / n
    d10 = sum(x == 1 and y == 0 for x, y in outcomes); d01 = sum(x == 0 and y == 1 for x, y in outcomes)
    rng = random.Random(20261018); diffs=[]
    for _ in range(10000):
        sample=[outcomes[rng.randrange(n)] for _ in outcomes]; diffs.append(sum(x-y for x,y in sample)/n)
    diffs.sort()
    return {"status":"SELF_TEST_ONLY_NOT_AGENT_DATA", "pairs": n, "discordances":{"c1_success_c2_failure":d10,"c1_failure_c2_success":d01}, "c1_rate":c1,"c2_rate":c2,"absolute_difference":abs(c1-c2),"bootstrap_95_ci":[diffs[250],diffs[9749]],"minimum_meaningful_absolute_difference":0.25}


def main() -> int:
    if OUT.exists(): raise SystemExit(f"refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)
    for name in ["stage0", "stage1/clean", "stage1/dev", "stage1/heldout", "stage1/private_truth", "stage1/labels", "schema_cases", "controls"]: (OUT/name).mkdir(parents=True, exist_ok=True)
    before = {str(p): sha_file(p) for p in PROTECTED}
    schema = json.loads(SCHEMA_PATH.read_text()); validator = Draft202012Validator(schema)

    # Independent Stage 0 replay: decode representations without calling the
    # original decoder and verify witnesses/ambiguity for exactly zero-query ECDSA/ChaCha20.
    stage0=[]
    for task, maker in [("ECDSA_Nonce_Reuse", base.make_ecdsa), ("ChaCha20_Nonce_Repeat", base.make_chacha)]:
        for seed in range(1,13):
            inst=maker(seed); c1=independent_decode(task,inst["c1"]); c2=independent_decode(task,inst["c2"])
            i1=base.interface_spec(task,"C1"); i2=base.interface_spec(task,"C2")
            core1={k:v for k,v in i1.items() if k not in {"condition","representation"}}; core2={k:v for k,v in i2.items() if k not in {"condition","representation"}}
            assert c1==c2 and core1==core2 and hobj(c1)==hobj(c2)
            assert i1["allowed_oracle_queries"]==i2["allowed_oracle_queries"] and i1["query_budget"]==i2["query_budget"] and i1["feedback"]==i2["feedback"] and i1["timeout_ms"]==i2["timeout_ms"]
            assert len(inst["ambiguity"])==2 and inst["ambiguity"][0]!=inst["ambiguity"][1]
            assert inst["witness"] and ("d" in inst["witness"] if task.startswith("ECDSA") else "plaintext_2" in inst["witness"])
            row={"task":task,"seed":seed,"semantic_hash_c1":hobj(c1),"semantic_hash_c2":hobj(c2),"interface_hash_c1":hobj(core1),"interface_hash_c2":hobj(core2),"allowed_queries":i1["allowed_oracle_queries"],"query_budget":i1["query_budget"],"feedback":i1["feedback"],"constructive_witness":inst["witness"],"ambiguity_counterexamples":inst["ambiguity"],"scope":"zero-query-only"}
            stage0.append(row); write_json(OUT/"stage0"/f"{task}_{seed:02d}.json",row)
    write_json(OUT/"stage0_summary.json", {"total":len(stage0),"ecdsa":12,"chacha20":12,"c1_c2_equivalence":len(stage0),"c0_ambiguity":len(stage0),"scope":"zero-query ECDSA/ChaCha20; no CBC/RC4 claim"})

    # Schema and runtime negatives.
    good, _, _ = make_cert(OUT/"schema_cases"/"valid", 1, "ECDSA_Nonce_Reuse", 1, True)
    cases=[("valid",good,True,True),("missing_evidence",copy.deepcopy(good),False,False),("invalid_identifier",copy.deepcopy(good),False,True),("mismatched_hash",copy.deepcopy(good),True,False),("invalid_version_binding",copy.deepcopy(good),True,False),("missing_boundary_kind",copy.deepcopy(good),True,False),("stale_run_id",copy.deepcopy(good),True,False)]
    cases[1][1].pop("evidence"); cases[2][1]["condition"]["id"]="C9"; cases[3][1]["evidence"][1]["sha256"]="0"*64
    bad_meta = OUT / "schema_cases" / "invalid_version_binding" / "verifier_metadata.json"; write_json(bad_meta, {"verifier_version":"stage01-reference-v999","implementation":"independent-reference-v1"})
    cases[4][1]["evidence"] = [dict(x) for x in cases[4][1]["evidence"]]
    for item in cases[4][1]["evidence"]:
        if item["kind"] == "verifier_metadata": item.update(path=str(bad_meta), sha256=sha_file(bad_meta))
    cases[5][1]["evidence"]=[x for x in cases[5][1]["evidence"] if x["kind"]!="boundary"]; cases[6][1]["execution"]["session_id"]="stale-session"
    schema_rows=[]
    for name,cert,expect_schema,expect_integrity in cases:
        errs=sorted(validator.iter_errors(cert),key=lambda e:list(e.path)); schema_ok=not errs; integ=True
        for item in cert.get("evidence",[]):
            p=Path(item["path"]); integ = integ and p.is_file() and sha_file(p)==item["sha256"]
        runtime_ok = runtime_integrity(cert)
        row={"case":name,"schema_valid":schema_ok,"expected_schema_valid":expect_schema,"integrity_valid":integ,"runtime_integrity_valid":runtime_ok,"expected_integrity_valid":expect_integrity,"schema_errors":[e.message for e in errs]}; schema_rows.append(row); write_json(OUT/"schema_cases"/f"{name}.json",{"certificate":cert,"result":row})
    assert all(r["schema_valid"]==r["expected_schema_valid"] for r in schema_rows)
    assert all(r["runtime_integrity_valid"] == r["expected_integrity_valid"] for r in schema_rows)
    write_json(OUT/"schema_validation_summary.json", {"schema_id":schema["$id"],"cases":schema_rows})

    # Generate clean controls and development defects. Labels are isolated files
    # and are never included in the reference bundle or public validator input.
    rows=[]; idx=1
    def evaluate(case_id, split, defect, valid, task, seed, case, cert, target_path, candidate_path):
        cert_path=case/"certificate.private.json"; write_json(cert_path,cert)
        bundle={"case_id":case_id,"target_state_path":str(target_path),"candidate_path":str(candidate_path),"certificate_path":str(cert_path)}
        bundle_path=case/"reference_input.json"; write_json(bundle_path,bundle)
        expected_label = "ACCEPTED" if (valid and defect == "none") else "REJECTED"
        label={"case_id":case_id,"stored_label":expected_label}
        if case_id in {"clean-01", "wrong_field-01"}: label["stored_label"]="REJECTED" if expected_label == "ACCEPTED" else "ACCEPTED"
        label_path=OUT/"stage1"/"labels"/f"{case_id}.json"; write_json(label_path,label)
        ref, ref_ms=invoke(REFERENCE,bundle_path); pub=public_cert(cert); public_path=case/"public_certificate.json"; write_json(public_path,pub)
        decision, val_ms=invoke(VALIDATOR,data=pub)
        forbidden_present=any(k in pub.get("verification",{}) for k in ["raw_verdict","reference_verdict","validator_verdict"]) or any(k in json.dumps(pub) for k in ["expected_reference_verdict","hidden_secret","defect_label"])
        generated_cert_errors = sorted(validator.iter_errors(cert), key=lambda e: list(e.path))
        if generated_cert_errors: raise AssertionError(f"generated certificate is not schema-valid: {case_id}: {[e.message for e in generated_cert_errors]}")
        row={"case_id":case_id,"split":split,"defect_family":defect,"primitive":task,"reference":ref,"validator":decision,"stored_label":label["stored_label"],"label_disagreement":ref["reference_verdict"]!=label["stored_label"],"public_forbidden_fields":forbidden_present,"reference_overhead_ms":ref_ms,"validator_overhead_ms":val_ms}
        rows.append(row); write_json(OUT/"stage1"/f"{split}_{case_id}.json",row); return row

    for n in range(10):
        task="ECDSA_Nonce_Reuse" if n%2==0 else "ChaCha20_Nonce_Repeat"; seed=n+1; case=OUT/"stage1"/"clean"/f"clean_{n+1:02d}"; cert,tp,cp=make_cert(case,idx,task,seed,True); evaluate(f"clean-{n+1:02d}","clean","none",True,task,seed,case,cert,tp,cp); idx+=1
    for n in range(10):
        task="ECDSA_Nonce_Reuse" if n%2==0 else "ChaCha20_Nonce_Repeat"; seed=n+21; case=OUT/"stage1"/"clean"/f"invalid_{n+1:02d}"; cert,tp,cp=make_cert(case,idx,task,seed,False); evaluate(f"invalid-{n+1:02d}","clean","none",False,task,seed,case,cert,tp,cp); idx+=1
    defects=["wrong_field","stale_binding","replay_cross_session","verifier_version_mismatch","interface_contamination"]
    for defect in defects:
        for variant in range(1,5):
            task="ECDSA_Nonce_Reuse" if variant%2 else "ChaCha20_Nonce_Repeat"; seed=100+idx; case=OUT/"stage1"/"dev"/defect/f"variant_{variant:02d}"; cert,tp,cp=make_cert(case,idx,task,seed,True); mutate(cert,case,defect,variant); evaluate(f"{defect}-{variant:02d}","dev",defect,True,task,seed,case,cert,tp,cp); idx+=1
    freeze_hash=sha_file(VALIDATOR); write_json(OUT/"controls"/"VALIDATOR_FREEZE.json",{"validator":str(VALIDATOR),"sha256_before_heldout":freeze_hash,"heldout_generation_after_freeze":True,"development_cases":20})
    for defect in defects:
        for variant in range(5,9):
            task="ECDSA_Nonce_Reuse" if variant%2 else "ChaCha20_Nonce_Repeat"; seed=200+idx; case=OUT/"stage1"/"heldout"/defect/f"variant_{variant:02d}"; cert,tp,cp=make_cert(case,idx,task,seed,True); mutate(cert,case,defect,variant); evaluate(f"{defect}-{variant:02d}","heldout",defect,True,task,seed,case,cert,tp,cp); idx+=1
    assert sha_file(VALIDATOR)==freeze_hash
    write_json(OUT/"controls"/"HELDOUT_FREEZE_CHECK.json",{"validator_sha256_before":freeze_hash,"validator_sha256_after":sha_file(VALIDATOR),"unchanged":sha_file(VALIDATOR)==freeze_hash,"heldout_cases":20})

    # All full certificates are schema-validated; aggregate independent metrics.
    for row in rows:
        cert=json.loads((OUT/"stage1"/row["split"]/(row["defect_family"] if row["defect_family"]!="none" else "")).read_text()) if False else None
    accepted_clean_valid=sum(r["validator"]["decision"]=="ACCEPT" for r in rows if r["case_id"].startswith("clean-")); rejected_invalid=sum(r["validator"]["decision"]=="REJECT" for r in rows if r["case_id"].startswith("invalid-"))
    defects=[r for r in rows if r["defect_family"]!="none"]; held=[r for r in defects if r["split"]=="heldout"]
    metrics={"total":len(rows),"clean_valid_accepted":accepted_clean_valid,"clean_invalid_rejected":rejected_invalid,"defects_rejected":sum(r["validator"]["decision"]=="REJECT" for r in defects),"heldout_rejected":sum(r["validator"]["decision"]=="REJECT" for r in held),"reference_validator_disagreements":sum(r["reference"]["reference_verdict"] != ("ACCEPTED" if r["validator"]["decision"]=="ACCEPT" else "REJECTED") for r in rows),"mislabeled_fixture_disagreements":sum(r["label_disagreement"] for r in rows),"public_forbidden_field_cases":sum(r["public_forbidden_fields"] for r in rows),"defect_by_family":{d:sum(r["validator"]["decision"]=="REJECT" for r in defects if r["defect_family"]==d) for d in ["wrong_field","stale_binding","replay_cross_session","verifier_version_mismatch","interface_contamination"]},"heldout_by_family":{d:sum(r["validator"]["decision"]=="REJECT" for r in held if r["defect_family"]==d) for d in ["wrong_field","stale_binding","replay_cross_session","verifier_version_mismatch","interface_contamination"]},"overhead_ms":{"reference_mean":sum(r["reference_overhead_ms"] for r in rows)/len(rows),"validator_mean":sum(r["validator_overhead_ms"] for r in rows)/len(rows)}}
    write_json(OUT/"stage1_results.json", {"rows":rows,"metrics":metrics})
    analysis=paired_analysis(); write_json(OUT/"paired_analysis_definition.json",analysis)
    after={str(p):sha_file(p) for p in PROTECTED}; assert before==after
    write_json(OUT/"protected_hashes.json",{"before":before,"after":after,"unchanged":before==after})
    write_json(OUT/"AGENT_EXECUTION_FREEZE.json",{"agent_calls_allowed":False,"provider_cost_ceiling_usd":0.0,"planned_sessions":72,"automatic_retries":0,"seed_replacement":False,"study_expansion":False,"status":"BLOCKED_PENDING_USER_APPROVAL","provider_calls_observed":0,"network_calls_observed":0})
    write_json(OUT/"run_manifest.json",{"protocol_commit":PROTOCOL_COMMIT,"reference":str(REFERENCE),"validator":str(VALIDATOR),"output":str(OUT),"model_calls":0,"provider_calls":0,"network_calls":0,"manuscript_modified":False,"result_locks_modified":False,"scope":"zero-query ECDSA/ChaCha20 deterministic controls only"})
    print(json.dumps({"output":str(OUT),"stage0":24,"stage1":len(rows),"metrics":metrics,"paired_analysis":analysis,"protected_unchanged":before==after},indent=2,sort_keys=True))
    return 0

if __name__ == "__main__": raise SystemExit(main())
