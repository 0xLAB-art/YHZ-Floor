import re

with open('encrypted', 'r', encoding='ascii') as f:
    ciphertext = bytes.fromhex(f.read())

key = b'A quart jar of oil mixed with zinc oxide makes a very bright paint|'
plaintext = bytes(c ^ key[i % len(key)] for i, c in enumerate(ciphertext))
flag, message, checksum = plaintext.split(b'|')
assert message + b'|' == key
assert re.fullmatch(rb'flag\{[^{}\r\n]+\}', flag)
assert re.fullmatch(rb'[0-9a-f]{32}', checksum)
print(flag.decode('ascii'))
