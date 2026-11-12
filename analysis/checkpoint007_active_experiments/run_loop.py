#!/usr/bin/env python3
"""Checkpoint 007 — local lab run loop. Reads key from ~/.config/acts007/apmix.key.
No secrets in prompts. Logs everything to 00_STATUS_AND_COST_LEDGER.md.
"""
import hashlib, json, os, subprocess, sys, time, csv, textwrap
from pathlib import Path
import requests

OUT = Path(__file__).resolve().parent
STAKE = 'PILOT'
ROOT = OUT.parents[2]
KEY = Path(os.path.expanduser('~/.config/acts007/apmix.key')).read_text().strip()
BASE = 'https://api.apmix.ai'
MODEL = 'claude-sonnet-4-6-free'

def log_event(kind, payload):
    t = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    row = {'time': t, 'kind': kind, 'payload': payload}
    (OUT / '00_STATUS_AND_COST_LEDGER.md').write_text(row.__str__()+'\n')  # keep one append-style
    print(kind, payload)

def attest():
    r = requests.get(f'{BASE}/v1/models', headers={'x-api-key': KEY, 'Authorization': f'Bearer {KEY}', 'anthropic-version': '2023-06-01'}, timeout=30)
    return r

def run(arm_id, prompt):
    r = requests.post(f'{BASE}/v1/messages', headers={'x-api-key': KEY, 'Authorization': f'Bearer {KEY}', 'anthropic-version': '2023-06-01', 'content-type': 'application/json'},
                      json={'model': MODEL, 'max_tokens': 256, 'messages': [{'role': 'user', 'content': prompt}]}, timeout=300)
    return r.json()

def spend_est(usage):
    # very rough placeholder: input $3/M tok, output $15/M tok (or provider pricing if available)
    return (usage.get('input_tokens',0)+usage.get('cache_read_input_tokens',0))*3/1e6 + usage.get('output_tokens',0)*15/1e6

def main():
    print('attestation:', attest().status_code, attest().json())
    print('run loop stub')
    sys.exit(0)
if __name__=='__main__':
    main()