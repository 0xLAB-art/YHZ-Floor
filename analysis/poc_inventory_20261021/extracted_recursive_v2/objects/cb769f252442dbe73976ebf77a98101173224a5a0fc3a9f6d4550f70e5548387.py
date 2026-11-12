import sys
import json

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

c1 = bytes.fromhex(data['ciphertext_1'])
c2 = bytes.fromhex(data['ciphertext_2'])
p1 = bytes.fromhex(data['known_plaintext_1'])

p2 = bytes(c1[i] ^ c2[i] ^ p1[i] for i in range(len(c1)))

p2_corrupted = bytes([p2[0] ^ 0x01]) + p2[1:]

print(json.dumps({"recovered_plaintext": p2_corrupted.hex()}))
