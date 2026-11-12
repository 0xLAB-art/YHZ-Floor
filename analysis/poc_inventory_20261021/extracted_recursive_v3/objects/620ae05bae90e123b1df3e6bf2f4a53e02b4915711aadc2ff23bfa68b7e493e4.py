import json, sys

c1_hex = "8a2934920d6aa24f4c7292c4f0fedb93c6d662386c1f7ba00affcf91e08ef11d47b812e03105c0ad4de88d14473ee40eb7457e628b6d2f1291811a1f8fd4007a"
c2_hex = "8955f9c31331c27ba8d6f9e999b65d71198a73d82a0998629f7d6e70ed6504bb67fbe6670b764d87f299721c13b92d1ad37760a9ab45945da05a9acc45a3fd81"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext2_hex = p1.hex()

# optional OPSPAN measurement could be here, but we omit

claim_line = "CLAIM:" + json.dumps({"plaintext2_hex": plaintext2_hex})
print(claim_line)
sys.stdout.flush()