import sys
import json

with open(sys.argv[1], 'r') as f:
    task = json.load(f)

c1_hex = task['public_input']['c1_hex']
c2_hex = task['public_input']['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1_xor_p2 = bytes(a ^ b for a, b in zip(c1, c2))

common_prefixes = [
    b'GET / HTTP/1.1\r\nHost: ',
    b'POST /api/login HTTP/1.1\r\n',
    b'{"username": "',
    b'{"message": "',
    b'Authorization: Bearer ',
    b'Cookie: session=',
    b'{"password": "',
    b'User-Agent: Mozilla/5.0 ',
]

for prefix in common_prefixes:
    if len(prefix) <= 64:
        p2_guess = prefix + b'\x00' * (64 - len(prefix))
        p1 = bytes(a ^ b for a, b in zip(p1_xor_p2, p2_guess))
        if all(32 <= b < 127 or b in (9, 10, 13) for b in p1[:len(prefix)]):
            print('CLAIM:' + json.dumps({'plaintext2_hex': p1.hex()}))
            sys.exit(0)

p2_guess = b'\x00' * 64
p1 = p1_xor_p2
print('CLAIM:' + json.dumps({'plaintext2_hex': p1.hex()}))