import json

c1_hex = "894aa6780e5a480ba373da91094de40bf47c0e20d466ec1a496b6ea501c3d2e66bed482f72c3535172a25bd996e592ac4a41b526398f28a18cd86f2d16e54bfe"
c2_hex = "ea665acfcf25ac3bdcd6ae78699a2713b9818f38cac975379d68cdc693901310c3e0b1286901d3b3eb837ad60a9dc4aeb253b7694fb5e41097864d10613c7d05"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
assert len(c1) == 64 and len(c2) == 64

p1 = bytes(a ^ b for a, b in zip(c1, c2))

print("CLAIM:" + json.dumps({"plaintext2_hex": p1.hex()}))