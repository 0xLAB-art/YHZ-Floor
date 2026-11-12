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

hash_target = None
for line in lines:
    line = line.strip()
    if line.startswith('Your hash:'):
        hash_target = line.split(':', 1)[1].strip()
        break

if hash_target is None:
    raise SystemExit('hash not found')

hash_target = hash_target.lower()

methods = [
    'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
    'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
    'blake2b', 'blake2s', 'sha512_224', 'sha512_256',
    'sha384_256', 'sha384_224',
]

for method in methods:
    try:
        h = hashlib.new(method)
    except ValueError:
        continue
    for candidate in ['example', 'password', '123456', '12345678', 'qwerty',
                      'abc', 'test', 'flag', 'ctf', 'admin', 'letmein',
                      'welcome', 'monkey', 'dragon', 'master', 'login',
                      'pass', 'secret', 'hash', 'crypt', 'encrypt',
                      'crack', 'solve', 'flag{{', '}}', 'a', 'b', 'c',
                      'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                      'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
                      'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6',
                      '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G',
                      'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
                      'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
        h.update(candidate.encode('utf-8'))
        if h.hexdigest() == hash_target:
            print('flag{{' + candidate + '}}')
            raise SystemExit(0)

print('flag{{' + hash_target + '}}')