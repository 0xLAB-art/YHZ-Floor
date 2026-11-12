#!/usr/bin/env python3
"""Diagnostic probe: the exact C2 prompt of an empty first-pass session,
sent ONCE through the frozen adapter at max_tokens=8000 (above the 4200 floor).
Records stop_reason / usage / text length; saves the raw body to this dir."""
import importlib.util, json, os, sys
from pathlib import Path

ROOT = Path('/mnt/nvme5/ACTS-Attack/sp2027/research_execution')
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('provider_adapter', ROOT/'provider_adapter_agentrouter_p023.py')
m = importlib.util.module_from_spec(spec); sys.modules['provider_adapter'] = m
spec.loader.exec_module(m)

os.environ['AGENTROUTER_LABEL_MODEL'] = 'gpt-6-astra'
prompt = (ROOT/'info_contract_aesgcm_random_p021ar_20261103/prompts/'
          'info_contract_aesgcm_random_p021ar_20261103__C2__seed_5434183162525103062__1b57f44fc462__turn1.txt').read_text()

p = m.ClaudeProvider()
try:
    r = p.call(prompt, 8000)
    txt = r.get('text','')
    print('OK text_len:', len(txt))
    print('head:', txt[:250].replace('\n',' '))
    raw = r.get('raw_body')
    if raw:
        (Path(__file__).parent/'probe_8000_ok.json').write_text(raw)
except m.ProviderFailure as e:
    print('ProviderFailure:', e.category, 'http', e.http_status)
    resp = getattr(e, 'response', None)
    raw = getattr(resp, 'raw', None) if resp else None
    body = getattr(resp, 'body', None) if resp else None
    if raw is None and body is not None:
        raw = getattr(body, 'content', None) or str(body)
    if isinstance(raw, bytes): raw = raw.decode('utf-8','replace')
    print('body excerpt:', (raw or '')[:400])
    if raw: (Path(__file__).parent/'probe_8000_fail.json').write_text(raw)
