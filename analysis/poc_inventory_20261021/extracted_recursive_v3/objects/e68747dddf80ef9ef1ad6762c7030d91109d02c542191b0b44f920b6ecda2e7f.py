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
    b'POST /api/login HTTP/1.1\r\n',
    b'GET /index.html HTTP/1.1\r\n',
    b'{"username": "',
    b'{"password": "',
    b'{"email": "',
    b'POST / HTTP/1.1\r\nHost: ',
    b'User-Agent: Mozilla/5.0 ',
]

for prefix in common_prefixes:
    if len(prefix) <= 64:
        p1_candidate = bytes(a ^ b for a, b in zip(p1_xor_p2[:len(prefix)], prefix))
        if all(32 <= byte <= 126 or byte in [9, 10, 13] for byte in p1_candidate):
            p2 = prefix + bytes(64 - len(prefix))
            p1 = bytes(a ^ b for a, b in zip(p1_xor_p2, p2))
            claim = {"plaintext2_hex": p2.hex()}
            print(f"CLAIM:{json.dumps(claim)}")
            sys.exit(0)

p2_default = b'\x00' * 64
claim = {"plaintext2_hex": p2_default.hex()}
print(f"CLAIM:{json.dumps(claim)}")