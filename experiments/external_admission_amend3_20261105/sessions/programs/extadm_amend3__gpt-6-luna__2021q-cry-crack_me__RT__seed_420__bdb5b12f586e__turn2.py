import base64
import hashlib
import json

with open('README.md', 'rb') as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw)
    text = decoded.decode('utf-8')
except Exception:
    text = raw.decode('utf-8', errors='replace')

hash_hex = None
for line in text.splitlines():
    line = line.strip()
    if line.startswith('Your hash:'):
        hash_hex = line.split(':', 1)[1].strip()
        break

if hash_hex is None:
    raise SystemExit('hash not found')

hash_hex = hash_hex.replace('\n', '').replace(' ', '')

hashes = [
    'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
    'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
    'blake2b', 'blake2s', 'sha512_224', 'sha512_256',
    'sha384_256', 'sha384_224', 'shake_128', 'shake_256',
]

for name in hashes:
    try:
        h = hashlib.new(name)
    except ValueError:
        continue
    if name.startswith('shake'):
        h.update(b'')
        continue
    h.update(b'')
    if h.hexdigest() == hash_hex:
        print(f'flag{{{name}}}')
        break
else:
    raise SystemExit('no match')
