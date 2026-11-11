import hashlib
import itertools
import re

with open('README.md', 'r', encoding='utf-8') as f:
    match = re.search(r'\b[0-9a-fA-F]{64}\b', f.read())
if match is None:
    raise RuntimeError('Hash not found')

target = bytes.fromhex(match.group(0))
algorithm = 'sha256'
salt = algorithm.encode('ascii')

def check(word):
    value = word.encode('utf-8')
    payloads = (
        value + salt,
        salt + value,
        value + b':' + salt,
        salt + b':' + value,
        value + b'$' + salt,
        salt + b'$' + value,
        value,
    )
    for payload in payloads:
        if hashlib.sha256(payload).digest() == target:
            print('flag{' + word + '}')
            raise SystemExit

roots = '''password 123456 12345678 qwerty abc123 letmein monkey dragon master football baseball shadow superman princess welcome sunshine iloveyou trustno1 admin secret hunter2 password1 password123 passcode passwd crackme crackthis hash hashcat sha256 crypto cryptography encryption decrypt security secure cybersecurity flag example challenge ctf salt salty john ripper rockyou correcthorsebatterystaple hello world test guest root access freedom computer matrix mustang batman jordan michael jennifer charlie thomas robert daniel george jessica ashley amanda nicole chelsea matthew anthony justin patrick richard jackson taylor william martin heather merlin diamond silver orange purple banana cookie chicken phoenix maverick falcon cowboy ferrari samsung arsenal eagles monster tiger yellow gateway bulldog porsche lakers london coffee boston mother forever winner winter prince angel flower wizard crystal panther canada unicorn rainbow starwars gandalf pokemon ninja killer soccer hockey ranger thunder hammer internet whatever qwertyuiop zxcvbnm asdfgh qazwsx 111111 000000 123123 654321 123456789 1234567890'''.split()

tails = ('', '1', '12', '123', '1234', '12345', '!', '!!', '@', '#', '007', '69', '99', '100', '101', '111', '321', '666', '777', '2020', '2021', '2022', '2023', '2024', '2025')
seen = set()
for root in roots:
    for stem in (root, root.lower(), root.capitalize(), root.upper()):
        for tail in tails:
            candidate = stem + tail
            if candidate not in seen:
                seen.add(candidate)
                check(candidate)

core = ('password', 'pass', 'word', 'hash', 'crack', 'crypto', 'cyber', 'security', 'secret', 'salt', 'flag', 'admin', 'root', 'super', 'dragon', 'master')
for left in core:
    for right in core:
        if left != right:
            for separator in ('', '_', '-', ' '):
                check(left + separator + right)

alphabet = 'abcdefghijklmnopqrstuvwxyz'
for length in range(1, 5):
    for chars in itertools.product(alphabet, repeat=length):
        check(''.join(chars))

raise RuntimeError('No candidate matched the supplied hash')
