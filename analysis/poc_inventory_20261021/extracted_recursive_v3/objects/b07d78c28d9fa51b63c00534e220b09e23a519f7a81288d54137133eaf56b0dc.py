import sys, json, os
sys.stderr.write('Reading from stdin...\n')
data = sys.stdin.read()
sys.stderr.write(f'Stdin length: {len(data)}\n')
sys.stderr.write(f'Stdin content: {repr(data)}\n')
sys.stderr.write('Environment:\n')
for k, v in sorted(os.environ.items()):
    if 'PROV' in k or 'SIG' in k or 'Z' in k or 'CHAL' in k:
        sys.stderr.write(f'{k}={v}\n')
try:
    if data.strip():
        parsed = json.loads(data.strip())
        sys.stderr.write(f'Parsed JSON keys: {list(parsed.keys())}\n')
except Exception as e:
    sys.stderr.write(f'Failed to parse JSON: {e}\n')
sys.stderr.flush()