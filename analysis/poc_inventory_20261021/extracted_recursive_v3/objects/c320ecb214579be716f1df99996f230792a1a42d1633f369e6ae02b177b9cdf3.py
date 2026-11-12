import sys
import json

c1_hex = "a3d11056b34e52e09e76f6bc3938b23d3022a1db73574ce77d693fcc07c622cdc439f6cb4d78cbec4dfd012aa74158dc75f76fcef6148cc2027778c803ca9ae9"
c2_hex = "ee38d2392815e6119da92794bb088a95b874c85673265544468f9ddcb76fe3068303194c2ae346040a2204288a6ff5a357c8996cdf0fac48b762d754e0cd9bb7"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# c2 is the keystream (encrypted zeros)
# P1 = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

claim = {"plaintext2_hex": p1.hex()}
print(f"CLAIM:{json.dumps(claim)}", flush=True)