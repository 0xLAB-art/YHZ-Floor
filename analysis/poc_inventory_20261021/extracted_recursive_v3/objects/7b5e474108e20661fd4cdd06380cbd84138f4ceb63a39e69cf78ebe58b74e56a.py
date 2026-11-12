import sys, json

c1_hex = "29440b99c3f60314cb22d51d62f5c08d9994c968944dfae8a70768ebbfa42a5f22ed8e5fed0e7edd8e19e2202236f3342fe87c6965a93b35954ff3b6448bea07"
c2_hex = "efb9279492edf43c7b4fb5e543999e7114ee878e550ff57c90c9393644e0dcdc0e1cd9afce40d4224405a5439fd30bbf0aea43336a487abad5fbed20eea48328"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# RC4 keystream is c2 (since c2 = RC4(key, 0x00*64))
ks = c2
# P1 = c1 XOR ks
p1 = bytes(a ^ b for a, b in zip(c1, ks))
plaintext_hex = p1.hex()

claim = {"plaintext_hex": plaintext_hex}
print(f"CLAIM:{json.dumps(claim)}")
# optionally OPSPAN_NS
import time
# measure maybe not needed