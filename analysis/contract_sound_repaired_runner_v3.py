#!/usr/bin/env python3
"""Fail-closed offline session state machine for future ACTS pilot runs.

Provider execution is intentionally not implemented/enabled here. This module
is the repaired per-session boundary used by deterministic tests and future
explicitly approved orchestration.
"""
from __future__ import annotations
import copy, importlib.util, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
_REPAIR_SPEC=importlib.util.spec_from_file_location('contract_sound_repaired_pipeline', HERE/'contract_sound_repaired_pipeline.py')
_repair=importlib.util.module_from_spec(_REPAIR_SPEC); _REPAIR_SPEC.loader.exec_module(_repair)
_RUNNER_SPEC=importlib.util.spec_from_file_location('pilot_runner_helpers', HERE/'run_contract_sound_agent_pilot_free_v2.py')
_runner=importlib.util.module_from_spec(_RUNNER_SPEC); _RUNNER_SPEC.loader.exec_module(_runner)
REFERENCE=HERE/'contract_sound_stage01_reference_verifier_v2.py'
VALIDATOR=HERE/'contract_sound_stage01_validator_v2.py'


def process_session(*, session_id: str, task: str, condition: str, seed: int, public_instance: dict, target_state: dict, candidate_source: str, case_dir: Path) -> dict:
    """Process one already-supplied candidate without provider access."""
    case_dir.mkdir(parents=True, exist_ok=False)
    manifest={"session_id":session_id,"task":task,"condition":condition,"seed":seed,"state_machine":"repaired-v3","provider_calls":0}
    (case_dir/'session_manifest.json').write_text(json.dumps(manifest,sort_keys=True)+'\n')
    execution=_repair.execute_candidate(candidate_source, public_instance, case_dir)
    result={"session_id":session_id,"task":task,"condition":condition,"seed":seed,"execution":execution,"reference":None,"validator":None}
    if execution.get('status') != 'EXECUTED':
        result['terminal_status']=execution.get('status','HARNESS_FAILURE')
        result['required_inputs_present']={"candidate_output":False,"target_state":True}
        (case_dir/'session_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        return result
    if not (case_dir/'candidate_output.json').is_file():
        result['terminal_status']='CANDIDATE_OUTPUT_MISSING'
        result['required_inputs_present']={"candidate_output":False,"target_state":True}
        (case_dir/'session_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        return result
    (case_dir/'target_state.private.json').write_text(json.dumps(target_state,sort_keys=True)+'\n')
    cert=_runner.make_certificate(case_dir,session_id,f'{task}-seed-{seed:02d}',task,condition,seed,execution,'OBSERVED')
    cert_path=case_dir/'certificate.private.json'; cert_path.write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n')
    bundle_path=case_dir/'reference_input.json'
    bundle_path.write_text(json.dumps({"case_id":session_id,"target_state_path":str(case_dir/'target_state.private.json'),"candidate_path":str(case_dir/'candidate_output.json'),"certificate_path":str(cert_path)},sort_keys=True)+'\n')
    reference=_repair.invoke_reference(REFERENCE,bundle_path)
    public=copy.deepcopy(cert); public.pop('verification',None); public['claims']['reference_oracle_acceptance']='NOT_ESTABLISHED'
    validator=_repair.invoke_validator(VALIDATOR,public)
    result['reference']=reference; result['validator']=validator
    if reference.get('reference_verdict')=='ACCEPTED' and validator.get('decision')=='ACCEPT':
        result['terminal_status']='ACCEPTED'
    elif reference.get('reference_verdict')=='REJECTED':
        result['terminal_status']='ORACLE_REJECTED'
    elif reference.get('reference_process') in {'FAILED','INVALID_OUTPUT'}:
        result['terminal_status']='REFERENCE_HARNESS_FAILURE'
    else:
        result['terminal_status']='VALIDATOR_REJECTED'
    (case_dir/'session_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result