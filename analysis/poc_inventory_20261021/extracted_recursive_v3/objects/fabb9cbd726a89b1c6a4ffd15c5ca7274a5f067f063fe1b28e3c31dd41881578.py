import json, sys

c1_hex = "5f8594bc59827c00403f58712880c99999c4d1302d9d681bc5f6b9a7d8fab2c8ae58a05a5717a30f9fdfae4ec560f68d579ddedacfc010fb3d9f96622c1331f2"
c2_hex = "f28f1ac2ceb4c3774f6df9abb52835b39ee6ce53d9005292c3559db7325deb9f8bd2b000972b471ea680ee7bfef9d45a43545c089818a9282c18e2ba879dfba2"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

pt = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = pt.hex()

claim = {"plaintext_hex": plaintext_hex}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()