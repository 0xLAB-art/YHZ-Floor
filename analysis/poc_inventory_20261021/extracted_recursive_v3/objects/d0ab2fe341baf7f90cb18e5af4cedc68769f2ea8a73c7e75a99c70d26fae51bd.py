import json, sys

c1 = bytes.fromhex("d9117f219874a1f3da954b932e8a23c687fab01663393ece929e43bf22ce6cb4aa4349a8afa563d1a30a775f7d513e26297fe10ca0a7d5e392360ccf964308f7")
c2 = bytes.fromhex("6cb810d4fbad564d109ea7cf7dd0af51bd8716b1b4325ca8ea3639f48ff2d7978d0e61ffaa7c14c29841fbe7a39fa603eb44e1dda0e60a2592259e9da702519a")

# Same key+nonce => same keystream: c1 XOR c2 = P1 XOR (0x00*64) = P1
p1 = bytes(a ^ b for a, b in zip(c1, c2))
assert len(p1) == 64

print("CLAIM:" + json.dumps({"plaintext2_hex": p1.hex()}))
sys.stdout.flush()