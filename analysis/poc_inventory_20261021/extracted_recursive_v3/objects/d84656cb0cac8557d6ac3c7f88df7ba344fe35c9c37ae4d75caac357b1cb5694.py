import sys
import json

c1_hex = "7968f263dc3a083e74355b30333999fadd8207ab80f17b93a4ea35136cdb181779575aeeb896ee0ebc9e91060bd36f14363b0b91c6341262a8460d56b177a504"
c2_hex = "bccbd61e0874acd23e93ef3072d8934e188d131de286105ac7538bf9f12960d0aeaa3326d3ced2719d4d0246ba412b94551ec706454864b3f3854fb2ff0b136f"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# Since P2 is all zeros, c2 = keystream
# P1 = c1 ^ keystream = c1 ^ c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

claim = {"plaintext_hex": p1.hex()}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()