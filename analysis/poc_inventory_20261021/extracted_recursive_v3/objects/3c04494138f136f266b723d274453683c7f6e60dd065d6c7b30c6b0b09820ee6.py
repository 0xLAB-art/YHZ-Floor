import sys

c1_hex = "075f745ae3896a07092ce083edde8999ee6d90a28ad6f81b4a3497a4f2ce2df782aa501c988d9bd26d93d77dccdde625e34a8dc8fdd3c2ea0bb203091cb50fa9"
c2_hex = "c599d571fd4e6d9f5f2c2ac6a7621e81402ebc390a9b164765e2729898f25269158e265b4d8b8f9a5a718361d7ab4dd8b0081243e391070bf24e70f7d89b63ab"

# Ensure same length
assert len(c1_hex) == len(c2_hex) == 128

# Convert to bytes
b1 = bytes.fromhex(c1_hex)
b2 = bytes.fromhex(c2_hex)

# XOR
p1 = bytes(a ^ b for a, b in zip(b1, b2))

plaintext_hex = p1.hex()
# claim
claim = {"plaintext_hex": plaintext_hex}
print(f"CLAIM:{__import__('json').dumps(claim)}")
sys.stdout.flush()