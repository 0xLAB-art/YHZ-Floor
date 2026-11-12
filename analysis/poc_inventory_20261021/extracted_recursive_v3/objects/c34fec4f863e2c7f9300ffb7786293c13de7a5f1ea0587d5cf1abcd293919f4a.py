import json, sys

c1_hex = "9198108002ab793b4a80ac5250c3981acdbc444e9a70cebdb02d67c59091b8b5901042b5436f80c9d5a5a12704229575b0f4ec227bb117147b61d79f25b27ce"
c2_hex = "d01debf1342aa6f944d3a4c72b58a1e917208295e769caaacd95548a78f4f0987d970f1f0bc839b403a64ac5dfcc5c760e7e6b1697b47a5946a809e3053b720f"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(x ^ y for x, y in zip(c1, c2))

claim = {"plaintext_hex": p1.hex()}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()