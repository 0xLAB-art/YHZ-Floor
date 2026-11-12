import base64
import hashlib
import json

with open('README.md', 'rb') as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw)
except Exception:
    decoded = raw

lines = decoded.decode('utf-8', errors='replace').splitlines()
hash_line = None
for line in lines:
    if 'hash:' in line.lower():
        hash_line = line
        break

if hash_line is None:
    raise SystemExit('no hash line found')

parts = hash_line.split(':', 1)
if len(parts) != 2:
    raise SystemExit('malformed hash line')

hash_value = parts[1].strip()

# Candidate hash algorithms in a plausible order
algorithms = [
    'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
    'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
    'blake2b', 'blake2s', 'md4', 'ripemd128', 'ripemd160',
    'ripemd256', 'ripemd320', 'whirlpool', 'tiger', 'gost',
    'shake_128', 'shake_256',
]

for algo in algorithms:
    try:
        h = hashlib.new(algo)
    except ValueError:
        continue
    h.update(hash_value.encode('utf-8'))
    digest = h.hexdigest()
    if digest == hash_value:
        print(f'flag{{{algo}}}')
        raise SystemExit(0)

raise SystemExit('no matching algorithm found')
