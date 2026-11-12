import sys, json, os
sys.stderr.write('=== Exploration ===\n')
sys.stderr.write(f'cwd: {os.getcwd()}\n')
sys.stderr.write(f'listdir: {os.listdir(".")}\n')
sys.stderr.write(f'argv: {sys.argv}\n')
# Check for any files in /tmp
try:
    tmp_files = os.listdir('/tmp')
    sys.stderr.write(f'/tmp files (first 20): {tmp_files[:20]}\n')
except Exception as e:
    sys.stderr.write(f'Cannot list /tmp: {e}\n')
# Check environment for any provision-like vars
for k, v in os.environ.items():
    if 'PROV' in k or 'SIG' in k or 'Z' in k or 'CHAL' in k or 'CURVE' in k:
        sys.stderr.write(f'ENV {k}={v}\n')
# Maybe the data is in a file passed as first argument?
if len(sys.argv) > 1:
    sys.stderr.write(f'First arg: {sys.argv[1]}\n')
    try:
        with open(sys.argv[1], 'r') as f:
            content = f.read()
            sys.stderr.write(f'File content: {content[:200]}\n')
    except Exception as e:
        sys.stderr.write(f'Cannot read arg file: {e}\n')
# Also check common names
for fname in ['provision.json', 'input.json', 'data.json', '/tmp/provision.json', '/tmp/input.json']:
    if os.path.exists(fname):
        sys.stderr.write(f'Found {fname}\n')
        try:
            with open(fname, 'r') as f:
                content = f.read()
                sys.stderr.write(f'Content: {content[:200]}\n')
        except Exception as e:
            sys.stderr.write(f'Error reading {fname}: {e}\n')
sys.stderr.flush()