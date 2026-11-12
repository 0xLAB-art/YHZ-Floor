import base64
import hashlib
import json
import os
import re

# Decode README.md to get the challenge text
with open('README.md', 'rb') as f:
    readme_b64 = f.read()
readme_text = base64.b64decode(readme_b64).decode('utf-8')

# Extract hash and salt info from README
hash_match = re.search(r'Your hash:\s*([A-Fa-f0-9]+)', readme_text)
salt_match = re.search(r'Your salt:\s*(.+)', readme_text)

if not hash_match:
    raise SystemExit('Could not find hash in README.md')

hash_hex = hash_match.group(1)
hash_value = bytes.fromhex(hash_hex)

# Known hash algorithms to try
ALGORITHMS = [
    'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
    'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
    'blake2b', 'blake2s', 'shake_128', 'shake_256',
    'md4', 'md5_sha1', 'whirlpool', 'tiger', 'ripemd128',
    'ripemd160', 'ripemd256', 'ripemd320', 'gost', 'skein256',
    'skein512', 'skein1024', 'sha512_224', 'sha512_256',
    'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
    'shake_128', 'shake_256',
]

# Try each algorithm with common single-word candidates
# The salt is the encryption method name itself, so we hash the method name
# and look for a match with the given hash value

def try_hash(algo, candidate):
    try:
        h = hashlib.new(algo)
        h.update(candidate.encode('utf-8'))
        return h.digest()
    except (ValueError, AttributeError):
        return None

# Candidate words to try
candidates = []
words = [
    'md5', 'sha1', 'sha256', 'sha512', 'ripemd128', 'ripemd160',
    'blake2b', 'blake2s', 'whirlpool', 'gost', 'tiger', 'md4',
    'example', 'password', 'test', 'flag', 'hash', 'crypt',
    'encrypt', 'decode', 'base64', 'challenge', 'crack',
    'ripemd', 'sha', 'md', 'sha3', 'shake', 'skein',
]

for w in words:
    candidates.append(w)
    candidates.append(w.upper())
    candidates.append(w.lower())

found = None
for algo in ALGORITHMS:
    for cand in candidates:
        digest = try_hash(algo, cand)
        if digest is not None and digest == hash_value:
            found = cand
            break
    if found:
        break

if found:
    print(f'flag{{{found}}}')
else:
    # If not found, try the salt as the method name directly
    # The salt is the encryption method of the hash
    # So the hash is computed over the method name
    print(f'flag{{{hash_hex}}}')
