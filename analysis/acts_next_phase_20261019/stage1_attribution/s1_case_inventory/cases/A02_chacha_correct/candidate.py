import json
import sys

inst = json.loads(sys.stdin.read())
c1 = bytes.fromhex(inst['ciphertext_1'])
c2 = bytes.fromhex(inst['ciphertext_2'])
p1 = bytes.fromhex(inst['known_plaintext_1'])
p2 = bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1))
print(json.dumps({'plaintext_2': p2.hex()}))
