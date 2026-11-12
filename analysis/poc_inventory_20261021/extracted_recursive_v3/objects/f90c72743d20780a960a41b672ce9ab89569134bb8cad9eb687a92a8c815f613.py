c1_hex = "89dc8f21413b3c1ba72e2e9a2233fb4f38edee0c369cb17b22e3e9b21f83fd4448ffec712f82bee2efb9c8203341e5a2dbeb5ab3daed59474872ce2551b98dc7"
c2_hex = "fd8e98a00d0d27727d079ce52c2fc44609b5f164a52e1c732e77edb0a4f6974e1192f64a58cda0f08dfdad6d2181a6f8dbe9c935d8d2229d1ce9170737"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# RC4 is a stream cipher: c1 = P1 XOR keystream, c2 = 0x00*64 XOR keystream = keystream
# Therefore P1 = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))
print(p1.hex())
print(p1)

import json
result = {"plaintext_hex": p1.hex()}
print(f"CLAIM:{json.dumps(result)}")