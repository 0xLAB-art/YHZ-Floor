import sys
import json

c1_hex = "7925036b881fd85e7d1b1990c85a01ccee78716ce23af0f0c53e8efb987e8e50294459bb1a877cdaf03fa5a0de8e0be5ce0fef57f88f098a6e67b918594069d8"
c2_hex = "bc0b62d1a039e14503b6a3aa9d0dd70e6b13235f90bb9e73e2945c22726fe1573ac4cb9e794f8c6861eb685914c3d8c7ff200e97945cd5b3401a303eb8fb5399"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# c2 is the keystream (since it's RC4(key, 0x00*64) = 0x00*64 XOR keystream = keystream)
# P1 = c1 XOR keystream = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

claim = {"plaintext_hex": p1.hex()}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()