#!/usr/bin/env python3
"""Build the blind GPT-family review payload for the Amend-3 decomposition.

Zero model calls here: this only compiles the frozen evidence into a compact,
self-contained payload. The reviewer prompt asks for independent derivations
under two stated counting rules; the reference (corrected) numbers are NOT in
the payload. Part B adjudicates printed claims after the blind part.
"""
import json
from pathlib import Path

NS = Path('/mnt/nvme5/ACTS-Attack/sp2027/research_execution/external_admission_amend3_20261105')
OUT = Path('/mnt/nvme5/ACTS-Attack/sp2027/analysis/amend3_decomposition_review_gpt_20261106')

rows = [json.loads(l) for l in (NS/'results.jsonl').read_text().splitlines() if l.strip()]
ANS = json.loads((NS/'oracle/answers.json').read_text())['answers']

def short_id(r):
    lab = r['label'].split('/')[-1].replace('free/','').split('-')[0]
    task = r['task_id'].split('cry-')[-1].replace('_','')
    return f"{lab}_{task}_{r['representation']}_{r['seed']}"

sessions = []
for r in rows:
    if r['status'] == 'PROVIDER_UNAVAILABLE':
        continue  # excluded slots are disclosed separately
    turns = []
    for t in r.get('turn_records', []):
        turns.append({
            'submitted': bool(t.get('submitted')),
            'returncode': t.get('returncode'),
            'timed_out': bool(t.get('timed_out')),
            'stage': t.get('stage'),
            'stdout_tail': (t.get('stdout_tail') or '')[:200],
            'stderr_tail': (t.get('stderr_tail') or '')[:140],
        })
    sessions.append({
        'id': short_id(r),
        'task': r['task_id'],
        'rep': r['representation'],
        'label': r['label'],
        'seed': r['seed'],
        'recorded_status': r['status'],
        'turns_in_order': turns,
    })

payload = {
    'oracle_pins_per_task': ANS,
    'excluded_slots_provider_unavailable': sum(1 for r in rows if r['status'] == 'PROVIDER_UNAVAILABLE'),
    'eps_task_statement_verbatim': 'Note: The flag is the entire thing decrypted',
    'sessions': sessions,
}
(OUT/'review_payload.json').write_text(json.dumps(payload, indent=0))
print('sessions in payload:', len(sessions))
print('payload bytes:', (OUT/'review_payload.json').stat().st_size)
