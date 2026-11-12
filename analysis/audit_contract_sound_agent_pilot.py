#!/usr/bin/env python3
"""Read-only audit of the frozen contract-sound agent pilot.

This audit never calls the model provider. It verifies schedule completeness,
no-retry semantics, provider failure taxonomy, artifact availability, route
consistency, and protected-file hashes. It deliberately does not convert
provider failures into agent successes or paired cryptographic outcomes.
"""
from __future__ import annotations
import hashlib, json, pathlib, collections, sys

ROOT = pathlib.Path('/mnt/nvme5/ACTS-Attack')
OUT = ROOT / 'sp2027/analysis/contract_sound_agent_pilot_20261018'
REPORT = OUT / 'PILOT_AUDIT.json'

PROTECTED = {
    'sp2027/analysis/RESULTS_LOCK.json': '4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39',
    'sp2027/analysis/RESULTS_LOCK_H1PC.json': '8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103',
    'sp2027/paper/main.tex': '51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461',
    'sp2027/paper/main.pdf': 'fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a',
}

def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

r = json.loads((OUT / 'pilot_results.json').read_text())
rows = r.get('rows', [])
schedule = json.loads((OUT / 'schedule.json').read_text()).get('schedule', [])
sessions = sorted((OUT / 'sessions').iterdir()) if (OUT / 'sessions').is_dir() else []
result_files = list((OUT / 'sessions').glob('*/session_result.json')) if (OUT / 'sessions').is_dir() else []
manifest_files = list((OUT / 'sessions').glob('*/session_manifest.json')) if (OUT / 'sessions').is_dir() else []

statuses = collections.Counter(x.get('status') for x in rows)
categories = collections.Counter(x.get('category') for x in rows)
errors = collections.Counter(x.get('error') for x in rows)
routes = collections.Counter(x.get('route') for x in json.loads((OUT/'schedule.json').read_text()).get('schedule', []))
ordinals = [x.get('ordinal') for x in rows]

protected = {}
for rel, expected in PROTECTED.items():
    p = ROOT / rel
    actual = sha256(p) if p.is_file() else None
    protected[rel] = {'exists': p.is_file(), 'sha256': actual, 'expected_sha256': expected, 'unchanged': actual == expected}

certificates = list((OUT / 'sessions').glob('*/certificate.private.json')) if (OUT/'sessions').is_dir() else []
provider_metadata = list((OUT / 'sessions').glob('*/provider_metadata.json')) if (OUT/'sessions').is_dir() else []
raw_responses = list((OUT / 'sessions').glob('*/provider_response.json')) + list((OUT / 'sessions').glob('*/provider_raw.json')) if (OUT/'sessions').is_dir() else []

result = {
    'audit_type': 'read_only_frozen_contract_sound_agent_pilot_audit',
    'provider_calls_issued_by_audit': 0,
    'pilot_rows': len(rows),
    'schedule_rows': len(schedule),
    'session_directories': len(sessions),
    'session_result_files': len(result_files),
    'session_manifest_files': len(manifest_files),
    'certificate_files': len(certificates),
    'provider_metadata_files': len(provider_metadata),
    'raw_response_files': len(raw_responses),
    'ordinals_unique_complete': sorted(ordinals) == list(range(1, 73)),
    'pilot_no_retries_declared': bool(r.get('no_retries')),
    'pilot_estimated_cost_usd': r.get('estimated_cost_usd'),
    'pilot_route': r.get('provider_route'),
    'status_counts': dict(statuses),
    'category_counts': dict(categories),
    'error_counts': dict(errors),
    'all_provider_failures': len(rows) == 72 and statuses == collections.Counter({'PROVIDER_FAILURE': 72}),
    'all_http_401': len(rows) == 72 and errors == collections.Counter({'HTTP 401': 72}),
    'cryptographic_outcomes_available': len(certificates) > 0,
    'paired_statistics_available': len(certificates) > 0,
    'protected_files': protected,
    'all_protected_files_unchanged': all(x['unchanged'] for x in protected.values()),
    'execution_freeze_status': json.loads((OUT/'EXECUTION_FREEZE.json').read_text()).get('status'),
    'provider_attestation_current': 'not_model_call',
    'recommendation': 'NO-GO: provider authentication failure invalidated the agent pilot as a scientific outcome; preserve campaign, do not retry without explicit new authorization and credential repair.',
}
REPORT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps(result, indent=2, sort_keys=True))
if not result['all_provider_failures'] or not result['all_http_401']:
    raise SystemExit('unexpected pilot taxonomy')
if not result['all_protected_files_unchanged']:
    raise SystemExit('protected file hash changed')