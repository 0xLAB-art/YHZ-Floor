import sys
import json

c1_hex = "c3921aa41a0dbaa577a6f70df09949cfb631886336e25aba1fe35f91308f0ee87d67e707829dc7e2204d57a613abb99813788c971e4e1282a284a7f288f0b6a2"
c2_hex = "e15ec98eb79e036c484a49e5f7f6d3ecf1cff534128ee093f41878690974a074aaecc6da76276d45d4d5f369422aab67e09c7e707e660f7531b13137333ef7f9"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# Since c2 = keystream (encrypting all zeros), P1 = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

claim = {"plaintext2_hex": p1.hex()}
print(f"CLAIM:{json.dumps(claim)}", flush=True)