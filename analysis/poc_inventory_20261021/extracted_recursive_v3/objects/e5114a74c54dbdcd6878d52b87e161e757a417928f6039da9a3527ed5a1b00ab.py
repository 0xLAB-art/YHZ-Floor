import sys
import json

c1_hex = "1f560a45455c2877d224db74fe5c01249b6fa26e56347d48ed08b03b15cf63665bc32b3867ade06f97297f3375248371b9dfc680b5730edf948ab6d4a60a9d41"
c2_hex = "4fca7a5ee537a27a6ef9bfb7b714dd7464637cb7b01aba8b2bb2b6995364b4a41fab85be03de8b67025931f7491983a49664a29ca7b2f250150c2b63390dfabd"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# Since c2 = RC4(key, 0x00*64) = keystream
# c1 = RC4(key, P1) = P1 XOR keystream
# Therefore P1 = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

claim = {"plaintext_hex": p1.hex()}
print(f"CLAIM:{json.dumps(claim)}", flush=True)