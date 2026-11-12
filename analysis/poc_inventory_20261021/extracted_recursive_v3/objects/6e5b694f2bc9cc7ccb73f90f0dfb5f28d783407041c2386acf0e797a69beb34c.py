import sys
import json

c1_hex = "3b4863090d03ff1c5b2e05bd8ae2b171f5e68a0522d1cdb732164d9fa9fe77d18c956d8cb3c63ef89fa80b7e25f7b216df99753b46ffa2fc009ef39ac71046cb"
c2_hex = "b8a2e5c27c4ee1422e82c0f551cae83e5da5c46065f4d1e6357128922ba8ac1f48f94d560b451b759d174118fd5d75b5d34f2332650deb97ea24ee96128134a1"

c1_bytes = bytes.fromhex(c1_hex)
c2_bytes = bytes.fromhex(c2_hex)

p1_bytes = bytes(a ^ b for a, b in zip(c1_bytes, c2_bytes))
p1_hex = p1_bytes.hex()

claim = json.dumps({"plaintext_hex": p1_hex})
print(f"CLAIM:{claim}")
sys.stdout.flush()