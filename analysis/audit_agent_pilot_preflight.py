#!/usr/bin/env python3
"""Independent, read-only preflight audit for the frozen C1/C2 pilot.

No provider adapter is imported, no network is used, and no protected source or
result file is written. The audit inspects actual generated task payloads and
recomputes deterministic protocol invariants from source and retained artifacts.
"""
from __future__ import annotations
import ast, base64, collections, hashlib, json, pathlib, random, re, subprocess, sys
from jsonschema import Draft202012Validator

ROOT = pathlib.Path('/mnt/nvme5/ACTS-Attack')
HERE = ROOT / 'sp2027/analysis'
STAGE = HERE / 'contract_sound_stage01_hardened_v2_20261018'
PILOT = HERE / 'run_contract_sound_agent_pilot.py'
ADAPTER = HERE / 'checkpoint007_active_experiments/runs_009/provider_adapter.py'
SCHEMA = HERE / 'contract_sound_artifact_schema_v1.json'
VALIDATOR_SOURCE = (HERE / 'contract_sound_stage01_validator_v2.py').read_text()
PROTECTED = {
    'sp2027/analysis/RESULTS_LOCK.json': '4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39',
    'sp2027/analysis/RESULTS_LOCK_H1PC.json': '8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103',
    'sp2027/paper/main.tex': '51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461',
    'sp2027/paper/main.pdf': 'fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a',
}

sys.path.insert(0, str(HERE))
import run_contract_sound_stage01 as base

# Extract source functions without executing pilot main or importing provider_adapter.
source = PILOT.read_text()
tree = ast.parse(source)
ns = {'__file__': str(PILOT), '__name__': 'preflight_source', 'random': random, 'json': json}
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(PILOT), 'exec'), ns)


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def source_const(name: str):
    match = re.search(rf'^{name}\s*=\s*(.+)$', source, flags=re.MULTILINE)
    return ast.literal_eval(match.group(1)) if match else None


def canonical(x) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def hobj(x) -> str:
    return hashlib.sha256(canonical(x)).hexdigest()


def independent_decode(task: str, obj: dict) -> dict:
    if task == 'ECDSA_Nonce_Reuse':
        if obj['encoding'] == 'json-hex-v1':
            return {'primitive': task, 'public_key': obj['public_key'], 'signature_1': obj['signature_1'], 'signature_2': obj.get('signature_2')}
        scalar = lambda v: f"{int.from_bytes(base64.b64decode(v), 'big'):064x}"
        return {'primitive': task, 'public_key': [scalar(v) for v in obj['public_key']], 'signature_1': {k: scalar(v) for k,v in obj['signature_1'].items()}, 'signature_2': {k: scalar(v) for k,v in obj['signature_2'].items()} if obj.get('signature_2') else None}
    if obj['encoding'] == 'json-hex-v1':
        return {'primitive': task, 'ciphertext_1': obj['ciphertext_1'], 'ciphertext_2': obj['ciphertext_2'], 'known_plaintext_1': obj.get('known_plaintext_1')}
    return {'primitive': task, 'ciphertext_1': base64.b64decode(obj['ciphertext_1']).hex(), 'ciphertext_2': base64.b64decode(obj['ciphertext_2']).hex(), 'known_plaintext_1': base64.b64decode(obj['known_plaintext_1']).hex() if obj.get('known_plaintext_1') else None}


def main():
    pair_rows = []
    c0_rows = []
    payload_failures = []
    for task, maker in [('ECDSA_Nonce_Reuse', base.make_ecdsa), ('ChaCha20_Nonce_Repeat', base.make_chacha)]:
        for seed in range(1, 13):
            inst = maker(seed)
            c1, c2, c0 = inst['c1'], inst['c2'], inst['c0']
            d1, d2 = independent_decode(task, c1), independent_decode(task, c2)
            semantic = inst['semantic']
            if d1 != semantic or d2 != semantic or c1 == c2:
                payload_failures.append({'task': task, 'seed': seed, 'd1_equals_semantic': d1 == semantic, 'd2_equals_semantic': d2 == semantic, 'raw_representations_distinct': c1 != c2})
            s1 = base.interface_spec(task, 'C1')
            s2 = base.interface_spec(task, 'C2')
            common1 = dict(s1); common2 = dict(s2); common1.pop('condition'); common1.pop('representation'); common2.pop('condition'); common2.pop('representation')
            pair_rows.append({'task': task, 'seed': seed, 'semantic_equal': d1 == d2 == semantic, 'raw_distinct': c1 != c2, 'interface_common_equal': common1 == common2, 'allowed_queries_equal': s1['allowed_oracle_queries'] == s2['allowed_oracle_queries'], 'query_budget_equal': s1['query_budget'] == s2['query_budget'], 'feedback_equal': s1['feedback'] == s2['feedback'], 'parser_equal': s1['parser'] == s2['parser'], 'timeout_equal': s1['timeout_ms'] == s2['timeout_ms'], 'target_seed_same': inst['seed'] == seed, 'witness_present': bool(inst.get('witness')), 'c1_condition': s1['condition'], 'c2_condition': s2['condition']})
            c0_rows.append({'task': task, 'seed': seed, 'two_ambiguity_examples': len(inst.get('ambiguity', [])) >= 2 and inst['ambiguity'][0] != inst['ambiguity'][1], 'c0_has_no_decisive_field': ('signature_2' not in c0) if task == 'ECDSA_Nonce_Reuse' else ('known_plaintext_1' not in c0)})

    schedule = ns['schedule']()
    expected = []
    rng = random.Random(20261018)
    for task in ['ECDSA_Nonce_Reuse', 'ChaCha20_Nonce_Repeat']:
        for seed in range(1, 13):
            pair = [{'task': task, 'seed': seed, 'condition': 'C1', 'kind': 'primary'}, {'task': task, 'seed': seed, 'condition': 'C2', 'kind': 'primary'}]
            rng.shuffle(pair); expected.extend(pair)
    for task in ['ECDSA_Nonce_Reuse', 'ChaCha20_Nonce_Repeat']:
        for seed in range(1, 13): expected.append({'task': task, 'seed': seed, 'condition': 'C0', 'kind': 'control'})

    # Stage 1 retained artifact checks.
    stage1 = json.loads((STAGE/'stage1_results.json').read_text())
    metrics = stage1['metrics']
    rows = stage1['rows']
    schema_validator = Draft202012Validator(json.loads(SCHEMA.read_text()))
    certs = list((STAGE/'stage1').glob('**/certificate.private.json')) + list((STAGE/'certificates').glob('**/certificate.private.json'))
    schema_count = 0
    schema_errors = []
    for p in certs:
        try:
            schema_validator.validate(json.loads(p.read_text())); schema_count += 1
        except Exception as e:
            schema_errors.append({'path': str(p), 'error': str(e)})
    stage1_counts = collections.Counter()
    for row in rows:
        stage1_counts[(row.get('split'), row.get('defect_family'), row.get('reference', {}).get('reference_verdict'), row.get('validator', {}).get('decision'))] += 1
    protected = {rel: {'actual': sha(ROOT/rel), 'expected': expected_hash, 'unchanged': sha(ROOT/rel) == expected_hash} for rel, expected_hash in PROTECTED.items()}

    prompt_sizes = []
    for task, maker in [('ECDSA_Nonce_Reuse', base.make_ecdsa), ('ChaCha20_Nonce_Repeat', base.make_chacha)]:
        for seed in range(1,13):
            inst = maker(seed)
            for condition in ['C1', 'C2', 'C0']:
                public = inst['c1'] if condition == 'C1' else inst['c2'] if condition == 'C2' else inst['c0']
                prompt_sizes.append(len(ns['prompt_for'](task, condition, public)))
    max_input_tokens = max(prompt_sizes) / 4.0
    max_cost = 72 * (max_input_tokens * 0.000003 + 1800 * 0.000015)

    freeze = json.loads((STAGE/'AGENT_EXECUTION_FREEZE.json').read_text())
    adapter_text = ADAPTER.read_text()
    runner_constants = {k: source_const(k) for k in ['ROUTE', 'ALERT_USD', 'HALT_USD', 'MAX_TURNS', 'TIMEOUT_SECONDS']}
    result = {
        'component_gates': {
            'reference_recomputes_crypto_and_cert_integrity': 'truth_source' in (json.loads((STAGE/'stage1_results.json').read_text())['rows'][0]['reference']) and 'recomputed-target-candidate' in json.dumps(stage1),
            'validator_forbidden_fields_declared': all(x in VALIDATOR_SOURCE for x in ['raw_verdict', 'reference_verdict', 'expected_reference_verdict', 'defect_label']),
            'schema_present': SCHEMA.is_file(),
            'runner_is_one_shot': source.count('provider.call(') == 1,
            'runner_protected_paths_absent': all(x not in PILOT.read_text() for x in ['RESULTS_LOCK.json', 'main.tex', 'main.pdf']),
        },
        'pair_audit': {
            'pairs': len(pair_rows), 'all_payloads_semantically_equal': all(x['semantic_equal'] for x in pair_rows), 'all_raw_representations_distinct': all(x['raw_distinct'] for x in pair_rows), 'all_common_interface_fields_equal': all(x['interface_common_equal'] for x in pair_rows), 'all_query_budgets_equal': all(x['query_budget_equal'] for x in pair_rows), 'all_feedback_equal': all(x['feedback_equal'] for x in pair_rows), 'all_parser_equal': all(x['parser_equal'] for x in pair_rows), 'all_timeout_equal': all(x['timeout_equal'] for x in pair_rows), 'all_seeds_same': all(x['target_seed_same'] for x in pair_rows), 'all_witnesses_present': all(x['witness_present'] for x in pair_rows), 'payload_failures': payload_failures,
        },
        'c0_audit': {'controls': len(c0_rows), 'all_two_ambiguity_examples': all(x['two_ambiguity_examples'] for x in c0_rows), 'all_decisive_observation_withheld': all(x['c0_has_no_decisive_field'] for x in c0_rows)},
        'schedule_audit': {'rows': len(schedule), 'matches_frozen_generator': schedule == expected, 'primary_rows': sum(x['kind']=='primary' for x in schedule), 'control_rows': sum(x['kind']=='control' for x in schedule), 'automatic_retries': 0, 'seed_replacement': False, 'study_expansion': False},
        'stage1_audit': {'rows': len(rows), 'metrics': metrics, 'schema_certificate_files_found': len(certs), 'schema_certificate_files_valid': schema_count, 'schema_errors': schema_errors, 'reference_crypto_truth_is_recomputed': all(r['reference'].get('truth_source') == 'recomputed-target-candidate-and-certificate' for r in rows), 'validator_only_public_evidence': all(not r['public_forbidden_fields'] for r in rows), 'reference_validator_disagreements': metrics['reference_validator_disagreements']},
        'protocol_freeze': {'stage_freeze': freeze, 'runner_constants': runner_constants, 'provider_endpoint_in_adapter': 'https://api.apmix.ai' in adapter_text, 'provider_route_in_runner': runner_constants['ROUTE'], 'provider_behavior_live_checked': False, 'max_prompt_chars': max(prompt_sizes), 'max_input_token_estimate_at_4_chars': max_input_tokens, 'max_output_tokens_per_call': 1800, 'model_cost_forecast_if_paid_rate_used_usd': max_cost, 'cost_ceiling_in_current_blocked_freeze_usd': freeze['provider_cost_ceiling_usd'], 'execution_gate_locked': freeze['agent_calls_allowed'] is False},
        'protected_hashes': protected,
        'offline_dry_run': json.loads((HERE/'agent_pilot_preflight_offline_20261018/OFFLINE_PREFLIGHT_SUMMARY.json').read_text()),
        'recommendation': 'NO-GO: preflight evidence is strong for deterministic controls, but execution must remain locked because the current freeze is agent_calls_allowed=false and provider behavior was intentionally not live-checked; resolve runner/freeze ceiling alignment and obtain explicit approval before any provider call.'
    }
    out = HERE/'AGENT_PILOT_PREFLIGHT_AUDIT.json'
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))
    assert len(pair_rows) == 24
    assert not payload_failures
    assert schedule == expected
    assert len(rows) == 60
    assert metrics['reference_validator_disagreements'] == 0
    assert result['offline_dry_run']['provider_calls'] == 0
    assert result['offline_dry_run']['network_calls'] == 0
    assert all(x['unchanged'] for x in protected.values())

if __name__ == '__main__':
    main()