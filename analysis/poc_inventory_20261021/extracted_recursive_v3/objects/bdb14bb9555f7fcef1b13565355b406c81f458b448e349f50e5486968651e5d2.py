import sys
import json

c1_hex = "77fc4867cd4a79f75d4bea4dfb488842a5e2004bbf22ff2633d2fb92ab4c73c855dda49fb8ac2699aae945d6893d0f247168b1b8667505ac36f6a228e257a730"
c2_hex = "c16038a0c1324c54e7258d923cf4e3c7fc3ae56f63da2dfdca8420bf3ca2ab7d2969a64d4751ee5f610e07bf5d5b5a6a7f34845ebeec9a593faad166d251d371"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1 = b'{"user_id": 1001, "role": "analyst", "clearance": "secret"}'

keystream = bytes(a ^ b for a, b in zip(c1, p1))
p2 = bytes(a ^ b for a, b in zip(c2, keystream))

print(json.dumps({"plaintext2_hex": p2.hex()}))