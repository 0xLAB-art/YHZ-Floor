import sys
import json

c1_hex = "dcd3c9f2e6333acdb40bfdc58614e644d9c0a1c631ed1405c8e293579a0b5389c0e39c9406a83d13376ce43fed69b4f5d70da6f22485e12fa05dc38a729ba87b"
c2_hex = "a55ec68bfdea5130e05e77f68e66b7907d57bccdbf0ab4d9cd8159dc967e4a5075b80e1f1e06160e74767e372d0538b1b623ea9ea303da80f5cfff573e7ae476"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# P1 = c1 XOR c2 (since c2 = keystream when plaintext is all zeros)
p1 = bytes(a ^ b for a, b in zip(c1, c2))

claim = {"plaintext2_hex": p1.hex()}
print(f"CLAIM:{json.dumps(claim)}")