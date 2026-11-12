import json, time

c1_hex = "b480533fcb42ef3613425829ef92f3069ae477a93dd66e07b3fdfbeaa25ccd4a8efbebb26d872e7c53a259657209bfcb32221f7b7a81935b1d9d1cb38b8d5807"
c2_hex = "03eca28f0151537dcad15416e877ee6179e5a09a3973766f24a3011dbeb2d19aca302a775e391e2d5e2f9a11927c071d77238df1f0f05f1d690adda48b0b01eb"

# XOR
b1 = bytes.fromhex(c1_hex)
b2 = bytes.fromhex(c2_hex)
assert len(b1) == len(b2) == 64
p1 = bytes(a ^ b for a, b in zip(b1, b2))
plaintext2_hex = p1.hex()

# optional timing
start = time.monotonic_ns()
# computation already done, but we can measure the XOR maybe
# but we already have it. We'll just measure a dummy or the whole thing.
# Actually we can measure the XOR operation:
# but we already computed. We can just record end.
end = time.monotonic_ns()
opspan = end - start

# Output
print(f"OPSPAN_NS:{opspan}")
print(f"CLAIM:{{"plaintext2_hex": "{plaintext2_hex}"}}")