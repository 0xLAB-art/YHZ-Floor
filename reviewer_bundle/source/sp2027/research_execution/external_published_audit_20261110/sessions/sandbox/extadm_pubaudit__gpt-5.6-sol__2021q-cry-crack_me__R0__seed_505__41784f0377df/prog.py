import hashlib
import itertools
import re
import string

with open('README.md', 'r', encoding='utf-8') as f:
    artifact = f.read()

match = re.search('[0-9A-Fa-f]{64}', artifact)
if match is None:
    raise RuntimeError('No 256-bit hexadecimal hash found')
target = bytes.fromhex(match.group(0))

methods = []
for name in sorted(hashlib.algorithms_available):
    try:
        probe = hashlib.new(name)
    except (TypeError, ValueError):
        continue
    if probe.digest_size == len(target):
        salt = ''.join(c for c in name.lower() if c.isalnum()).encode()
        methods.append((name, salt))

common = '''password 123456 123456789 qwerty 12345678 111111 1234567890 1234567 password1 123123 12345 iloveyou 1234 000000 qwerty123 abc123 1q2w3e4r admin qwertyuiop 654321 555555 lovely 7777777 welcome 888888 princess dragon password123 123qwe football monkey letmein shadow master baseball superman trustno1 sunshine princess1 passw0rd starwars freedom whatever qazwsx mustang michael ninja soccer charlie asdfgh asdfghjkl hunter killer secret flower hello computer cookie cheese orange banana pepper pokemon batman matrix root toor crackme crackthis hash hashcat hashing salted salt crypto cryptography cipher encryption decryption security cybersecurity flag capturetheflag ctf example correcthorsebatterystaple hunter2 swordfish open sesame opensesame supersecret changeme default guest login access internet windows linux ubuntu kali rockyou'''.split()

suffixes = ('', '1', '12', '123', '1234', '!', '01', '007', '69', '99', '2000', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024')

def candidates():
    seen = set()
    for base in common:
        forms = (base, base.lower(), base.capitalize(), base.upper())
        for form in forms:
            for suffix in suffixes:
                candidate = form + suffix
                if candidate not in seen:
                    seen.add(candidate)
                    yield candidate
    for length in range(1, 6):
        for chars in itertools.product(string.ascii_lowercase, repeat=length):
            candidate = ''.join(chars)
            if candidate not in seen:
                yield candidate

answer = None
separators = (b'', b':', b'$', b'|', b'-', b'_')
for candidate in candidates():
    word = candidate.encode()
    for method, salt in methods:
        for separator in separators:
            payloads = (word + separator + salt, salt + separator + word)
            if any(hashlib.new(method, payload).digest() == target for payload in payloads):
                answer = candidate
                break
        if answer is not None:
            break
    if answer is not None:
        break

if answer is None:
    raise RuntimeError('No candidate matched the salted hash')
print('flag{' + answer + '}')
