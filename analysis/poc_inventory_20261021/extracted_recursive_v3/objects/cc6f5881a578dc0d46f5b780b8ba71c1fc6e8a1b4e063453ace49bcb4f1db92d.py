import binascii

c1_hex = "6768d62dc28da327abd37ea8165149543c4d4dd6dd60fd339db0119e357808fb9f0a22b305b6f8556c333de4bbb35e2fcf1ae96b0c3b0e09b1ae969a04e6100"
c2_hex = "a122bc1a1f0c07e2a611a830698d3a3fdea8b4be6bc038961c68d292cc92358bf736930c85841bb50b31c0d2d043c015543e375480b56cdbe8e96a1842a9e467"

c1 = binascii.unhexlify(c1_hex)
c2 = binascii.unhexlify(c2_hex)

# RC4 keystream reuse: c2 = keystream (since plaintext is all zeros)
# P1 = c1 XOR keystream = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

p1_hex = p1.hex()
print(f"plaintext_hex: {p1_hex}")
print(f"length: {len(p1)} bytes")
print(f"CLAIM: {{\"plaintext_hex\": \"{p1_hex}\"}}")