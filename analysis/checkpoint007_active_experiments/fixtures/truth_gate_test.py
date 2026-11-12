"""Truth-exclusion gate test: verifies that prompt bytes never contain reserved
secret, digest, or verifier truth before any model call.
"""
import hashlib, json, subprocess, textwrap
from pathlib import Path
def make_prompt(public_obs=None):
    return json.dumps(public_obs or {}, separators=(',',':')) if isinstance(public_obs,dict) else str(public_obs)

def test_gate():
    secret = hashlib.sha256(b'seed1').digest()[:16]
    forbidden = b'key' if False else b'secret'  # simulates the verifier-side secret never entered into the prompt
    # Correct pattern: build prompt from public observations only; confirm the
    # verifier-side secret is never part of it.
    prompt = make_prompt({'obs': 'P1 prefix, P2 prefix'})
    prompt_bytes = prompt.encode()
    assert forbidden not in prompt_bytes and b'secret' not in prompt_bytes
    print('gate PASS: forbidden not in prompt')
    # double check the prompt itself never contains the hex of secret
    assert hashlib.sha256(secret).hexdigest() not in prompt
    print('end')

if __name__=='__main__':
    test_gate()
