import time

c1_hex = "aed78b6669b1588b3d96efcf624e1578d2825e913329e865213e7a983eda3deb04b0ef4f872cb4fe9fd73748cbddfd7147c85c129929e95598cccc5c7d66c9de"
c2_hex = "6755a28e32d37ca9412bd0cce1c89144b2ab276dd29ecdea2633a4c199a500c4451f3abd06a6ead7ea8cbf44677bfba97e5647205198ef2d5746f1078995aac8"

t0 = time.monotonic_ns()

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# RC4 is a stream cipher: C = P XOR Keystream.
# c1 = P1 XOR S ; c2 = 0x00*64 XOR S = S
# => P1 = c1 XOR c2  (keystream cancels)
p1 = bytes(a ^ b for a, b in zip(c1, c2))

# self-check: P1 XOR S must reproduce c1, and S must equal c2
S = c2
assert bytes(x ^ y for x, y in zip(p1, S)) == c1

span = time.monotonic_ns() - t0

print('OPSPAN_NS:%d' % span)
print('CLAIM:{"plaintext_hex": "%s"}' % p1.hex())