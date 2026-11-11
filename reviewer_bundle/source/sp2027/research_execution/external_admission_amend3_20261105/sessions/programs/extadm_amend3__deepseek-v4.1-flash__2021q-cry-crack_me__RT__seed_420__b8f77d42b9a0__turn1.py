import base64
import hashlib
import json
import os

with open('README.md', 'rb') as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw)
    text = decoded.decode('utf-8')
except Exception:
    text = raw.decode('utf-8', errors='replace')

hash_hex = 'a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c'

# Candidate hash algorithms (hashlib names)
candidates = [
    'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
    'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
    'blake2b', 'blake2s', 'sha512_224', 'sha512_256',
    'sha3_224', 'shake_128', 'shake_256',
    'md4', 'md2', 'ripemd128', 'ripemd160', 'whirlpool',
]

# Common wordlist candidates (lowercase)
words = [
    'password', 'admin', 'root', 'test', 'flag', 'example', 'secret',
    'letmein', 'welcome', 'monkey', 'dragon', 'master', 'qwerty',
    'login', 'passw0rd', 'hello', 'charlie', 'donald', 'superman',
    'trustno1', 'football', 'baseball', 'iloveyou', 'sunshine',
    'princess', 'shadow', 'michael', 'jennifer', 'thomas', 'jordan',
    'andrew', 'maggie', 'hunter', 'rachel', 'pepper', 'jessica',
    'shadow', 'shadow1', 'shadow2', 'shadow3', 'shadow4', 'shadow5',
    'shadow6', 'shadow7', 'shadow8', 'shadow9', 'shadow10',
    'test123', '123456', '12345678', '123456789', '12345', '1234567',
    '1234567890', 'abc123', 'password1', 'password123', 'admin123',
    'root123', 'test1234', 'pass123', 'pass1234', 'pass12345',
    'pass123456', 'pass1234567', 'pass12345678', 'pass123456789',
    'pass1234567890', 'pass12345678901', 'pass123456789012',
    'pass1234567890123', 'pass12345678901234', 'pass123456789012345',
    'pass1234567890123456', 'pass12345678901234567', 'pass123456789012345678',
    'pass1234567890123456789', 'pass12345678901234567890',
]

# Also try the hash hex itself and common variants
words += [hash_hex, hash_hex[:8], hash_hex[:12], hash_hex[:16], hash_hex[:20], hash_hex[:24], hash_hex[:32]]
words += ['a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c']

# Try each algorithm with each word
for algo in candidates:
    try:
        h = hashlib.new(algo)
    except (ValueError, TypeError):
        continue
    for word in words:
        h.update(word.encode('utf-8'))
        if h.hexdigest() == hash_hex:
            print(f'flag{{{word}}}')
            raise SystemExit

# Try uppercase variants of words
for algo in candidates:
    try:
        h = hashlib.new(algo)
    except (ValueError, TypeError):
        continue
    for word in words:
        for variant in [word.upper(), word.capitalize(), word.title()]:
            h.update(variant.encode('utf-8'))
            if h.hexdigest() == hash_hex:
                print(f'flag{{{variant}}}')
                raise SystemExit

# Try numbers 1-10000
for algo in candidates:
    try:
        h = hashlib.new(algo)
    except (ValueError, TypeError):
        continue
    for n in range(1, 10001):
        h.update(str(n).encode('utf-8'))
        if h.hexdigest() == hash_hex:
            print(f'flag{{{n}}}')
            raise SystemExit

# If nothing found, print the hash and algo for debugging
print('No match found')
print(json.dumps({'hash': hash_hex, 'algorithms_tried': candidates}))
