import hashlib, re

with open('README.md', 'r', encoding='utf-8') as f:
    target = re.search('[0-9A-Fa-f]{64}', f.read()).group(0).lower()

salt = b'sha256'
candidates = '''password Password PASSWORD password1 passw0rd 123456 123456789 qwerty abc123 letmein welcome monkey dragon master secret admin login hashcat crackme hunter2 iloveyou sunshine princess football'''.split()

for candidate in candidates:
    word = candidate.encode()
    salted_values = (word + salt, salt + word, word + b':' + salt, salt + b':' + word)
    if any(hashlib.sha256(value).hexdigest() == target for value in salted_values):
        print('flag{' + candidate + '}')
        break
else:
    raise RuntimeError('No verified preimage found')
