#!/usr/bin/env python3
"""Offline deterministic stand-in for the frozen 72-session pilot.

No provider adapter is imported and no network/model call is possible. The
stand-in returns precomputed valid candidates for C1/C2 and an explicit
UNDERDETERMINED object for C0, then exercises the same sandbox, certificate,
reference-verifier, blind-validator, schema, and accounting paths in an
isolated output directory.
"""
from __future__ import annotations
import copy, hashlib, json, pathlib, shutil, subprocess, sys, tempfile
from jsonschema import Draft202012Validator

ROOT = pathlib.Path('/mnt/nvme5/ACTS-Attack')
HERE = ROOT / 'sp2027/analysis'
OUT = HERE / 'agent_pilot_preflight_offline_20261018'
BASE = HERE / 'run_contract_sound_stage01.py'
PILOT = HERE / 'run_contract_sound_agent_pilot.py'
REFERENCE = HERE / 'contract_sound_stage01_reference_verifier_v2.py'
VALIDATOR = HERE / 'contract_sound_stage01_validator_v2.py'
SCHEMA = HERE / 'contract_sound_artifact_schema_v1.json'

sys.path.insert(0, str(HERE))
import run_contract_sound_stage01 as base
# Import only local harness functions, never provider_adapter.
spec = {'__file__': str(PILOT), '__name__': 'offline_runner_source'}
exec(compile(PILOT.read_text(), str(PILOT), 'exec'), spec)


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: pathlib.Path) -> str:
    return sha_bytes(p.read_bytes())


def canonical(x) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def hobj(x) -> str:
    return sha_bytes(canonical(x))


def write_json(p: pathlib.Path, x) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + '\n')


def invoke(script: pathlib.Path, payload: pathlib.Path | dict) -> dict:
    if isinstance(payload, pathlib.Path):
        argv = [sys.executable, str(script), str(payload)]
        proc = subprocess.run(argv, capture_output=True, text=True, check=False)
    else:
        proc = subprocess.run([sys.executable, str(script)], input=json.dumps(payload), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f'{script.name}: rc={proc.returncode}: {proc.stderr}')
    return json.loads(proc.stdout)


def candidate_source(task: str, condition: str, seed: int) -> str:
    if condition == 'C0':
        return 'import json\nprint(json.dumps({"status":"UNDERDETERMINED","reason":"decisive observation absent"}))\n'
    inst = base.make_ecdsa(seed) if task == 'ECDSA_Nonce_Reuse' else base.make_chacha(seed)
    if task == 'ECDSA_Nonce_Reuse':
        candidate = {'d': f"{inst['hidden']['d']:064x}", 'k': f"{inst['hidden']['k']:064x}"}
    else:
        candidate = {'plaintext_2': inst['witness']['plaintext_2']}
    return 'import json\nprint(json.dumps(' + repr(candidate).replace("'", '"') + '))\n'


def make_target(task: str, seed: int) -> dict:
    inst = base.make_ecdsa(seed) if task == 'ECDSA_Nonce_Reuse' else base.make_chacha(seed)
    return {'primitive': task, **inst['semantic']}


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'sessions').mkdir(parents=True)
    schema_validator = Draft202012Validator(json.loads(SCHEMA.read_text()))
    schedule = spec['schedule']()
    rows = []
    reference_counts = {'ACCEPTED': 0, 'REJECTED': 0}
    validator_counts = {'ACCEPT': 0, 'REJECT': 0}
    schema_valid = 0
    for ordinal, item in enumerate(schedule, 1):
        sid = f'offline-contract-sound-{ordinal:03d}'
        case = OUT / 'sessions' / sid
        case.mkdir()
        task, seed, condition = item['task'], item['seed'], item['condition']
        inst = base.make_ecdsa(seed) if task == 'ECDSA_Nonce_Reuse' else base.make_chacha(seed)
        public = inst['c1'] if condition == 'C1' else inst['c2'] if condition == 'C2' else inst['c0']
        prompt = spec['prompt_for'](task, condition, public)
        write_json(case / 'session_manifest.json', {'ordinal': ordinal, 'session_id': sid, 'task': task, 'seed': seed, 'condition': condition, 'kind': item['kind'], 'route': 'offline-deterministic-stand-in', 'prompt_sha256': sha_bytes(prompt.encode()), 'input_hash': hobj(public)})
        source = candidate_source(task, condition, seed)
        execution = spec['execute_candidate'](source, public, case)
        if condition == 'C0':
            target_status = 'OBSERVED' if execution.get('status') == 'EXECUTED' else 'NOT_OBSERVED'
        else:
            target_status = 'OBSERVED' if execution.get('status') == 'EXECUTED' else 'NOT_OBSERVED'
        cert = spec['make_certificate'](case, sid, f'{task}-seed-{seed:02d}', task, condition, seed, execution, target_status)
        cert_path = case / 'certificate.private.json'
        write_json(cert_path, cert)
        target_path = case / 'target_state.private.json'
        write_json(target_path, make_target(task, seed))
        bundle = case / 'reference_input.json'
        write_json(bundle, {'case_id': sid, 'target_state_path': str(target_path), 'candidate_path': str(case / 'candidate_output.json'), 'certificate_path': str(cert_path)})
        reference = invoke(REFERENCE, bundle)
        public_cert = copy.deepcopy(cert)
        public_cert.pop('verification', None)
        public_cert['claims']['reference_oracle_acceptance'] = 'NOT_ESTABLISHED'
        validator = invoke(VALIDATOR, public_cert)
        schema_validator.validate(cert)
        schema_valid += 1
        reference_counts[reference['reference_verdict']] += 1
        validator_counts[validator['decision']] += 1
        write_json(case / 'offline_result.json', {'reference': reference, 'validator': validator, 'execution': execution, 'provider_calls': 0, 'estimated_cost_usd': 0.0})
        rows.append({'ordinal': ordinal, 'task': task, 'seed': seed, 'condition': condition, 'reference': reference['reference_verdict'], 'validator': validator['decision'], 'execution': execution['status'], 'provider_calls': 0})
    summary = {
        'mode': 'offline-deterministic-stand-in', 'provider_calls': 0, 'network_calls': 0, 'estimated_cost_usd': 0.0,
        'rows': len(rows), 'schedule_seed': 20261018, 'schema_valid_certificates': schema_valid,
        'reference_counts': reference_counts, 'validator_counts': validator_counts,
        'c1_c2_reference_accepted': sum(r['reference'] == 'ACCEPTED' for r in rows if r['condition'] in {'C1','C2'}),
        'c0_reference_rejected': sum(r['reference'] == 'REJECTED' for r in rows if r['condition'] == 'C0'),
        'all_provider_calls_zero': all(r['provider_calls'] == 0 for r in rows),
        'all_session_results_present': all((OUT/'sessions'/f"offline-contract-sound-{i:03d}"/'offline_result.json').is_file() for i in range(1,73)),
    }
    write_json(OUT / 'OFFLINE_PREFLIGHT_SUMMARY.json', summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    assert summary['rows'] == 72
    assert summary['schema_valid_certificates'] == 72
    assert summary['all_provider_calls_zero']
    assert summary['all_session_results_present']
    assert summary['c1_c2_reference_accepted'] == 48
    assert summary['c0_reference_rejected'] == 24
    return 0

if __name__ == '__main__':
    raise SystemExit(main())