import sys
import json

c1_hex = "1601d3e588aecc076afc3318f2add8def6f47d81625193ad583e3eec3f06eb556f692e2165250fe5d72e5dc8ccc0d5cb59209954abb100cc547490b3607f0864"
c2_hex = "55f37c62a0edbf89cc675fc2f3fd4193348645fa8c2dcacb673495ec13c58645b205a14c7a945869c889a54fa79ac1c99483c39276fdcff7791a50e27423f5ea"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# Since c2 = RC4(key, 0x00 * 64) = keystream
# And c1 = RC4(key, P1) = P1 XOR keystream
# Therefore P1 = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

claim = {"plaintext_hex": p1.hex()}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()