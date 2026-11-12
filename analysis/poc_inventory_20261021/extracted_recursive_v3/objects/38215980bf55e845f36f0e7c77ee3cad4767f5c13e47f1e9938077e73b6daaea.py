import sys
import json

c1_hex = "2ece1729d8c7e0b05cc22336894fff57148775a438ff0f47c485978181b23ab19f207455a9cdc6c84111e4b39083bd432d6cf1d0711ada29fa733e65052a6375"
c2_hex = "daaa0d50a24ab4f07497c03bced963aa971caf01f5f2bf20a09f89b5f3dfb505019010f483dc7eae7163a43e7cd5f6d8f1512aa5a8471e6f30a905fcaaf995b3"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# Since c2 = keystream (encrypting all zeros), P1 = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

claim = {"plaintext2_hex": p1.hex()}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()