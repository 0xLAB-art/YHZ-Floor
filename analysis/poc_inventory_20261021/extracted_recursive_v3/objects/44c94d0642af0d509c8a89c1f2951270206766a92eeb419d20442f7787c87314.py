import sys
import json

def main():
    c1_hex = "f623eb535da9813e6175d4c6c17246b67f63191bf774696e939f3cc89f8b107ed3f4bd0eb1fa175a467aed9b0c963d8f92ba2a7278f0fb831e08fffcbd93737c"
    c2_hex = "58633d280b352ee26e78581b18c253736ba0cdae433135308307e478b62e6119fe83f2dede8fb9fbd05731f4d3be187e8890e0fb2cd209c317c625084c00044b"
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # Since c2 = keystream (encryption of zeros), P1 = c1 XOR c2
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    
    claim = {"plaintext2_hex": p1.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()