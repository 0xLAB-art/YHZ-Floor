import json
c1 = bytes.fromhex("832173ca5db05dd28707bc82e02cadcc664a9f45e8471e68899f4f7841877265be7cca42499e62302d420a11ca933c4547532db40de75c57093e602625267e66")
c2 = bytes.fromhex("ba099c24b444950ed4559f82c4ff74e776d4eb4d84ba796d6801ea442cb8324453f6d565910a1d05bcb3f833bb634d96ba8a71554e624d916b523022781a1091")
import time
t0 = time.monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(c1, c2))
opspan = time.monotonic_ns() - t0
print("OPSPAN_NS:" + str(opspan))
print("CLAIM:" + json.dumps({"plaintext2_hex": p1.hex()}))