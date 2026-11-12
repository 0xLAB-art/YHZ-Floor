import json

c1_hex = '56bca38023f18693caa7d793b0eb4cf52074463b99204666541e611ec662d49f946cc44c226c1cd50d65a2dcc8a0838c341a4a6d9bd98e97c6e0f9c48ef239e2'
c2_hex = '389a724e6d66972a118467bc19565ae79b1918288a7c0587053682be577050b0267439faea19df6abeb45c094234277b274fc8aacb87b5e2171bcaaa2fa09f3b'

# Convert hex to bytes
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# RC4 keystream reuse attack:
# c2 = RC4(key, 0x00*64) = keystream (since plaintext is all zeros)
# c1 = RC4(key, P1) = P1 XOR keystream
# Therefore: P1 = c1 XOR c2

p1 = bytes(a ^ b for a, b in zip(c1, c2))
p1_hex = p1.hex()

claim = {"plaintext_hex": p1_hex}
print(f'CLAIM:{json.dumps(claim)}')