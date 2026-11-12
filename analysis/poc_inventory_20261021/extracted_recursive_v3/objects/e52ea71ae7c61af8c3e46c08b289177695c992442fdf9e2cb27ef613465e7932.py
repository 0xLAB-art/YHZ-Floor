import sys
import json

c1_hex = "12ba72b49909ad690694a256744d0b0d649a6f91be2808cb209f9fe494820de6d84241420f551f9674cc77bca2c9de01d3097642e3ac56ba7cbddef54f6c4d4b"
c2_hex = "68bd8eb9d4b771b84600828fa931ebacea3e410c42ecd4c3f706623edf620480926cf9f55197ded54a0bb5e2582b54985d0b5777844103c0ab53f393ae329f5b"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# Since c2 = RC4(key, 0x00*64) = keystream
# And c1 = RC4(key, P1) = P1 ^ keystream
# Therefore P1 = c1 ^ c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

print(f'CLAIM:{{"plaintext_hex": "{p1.hex()}"}}')