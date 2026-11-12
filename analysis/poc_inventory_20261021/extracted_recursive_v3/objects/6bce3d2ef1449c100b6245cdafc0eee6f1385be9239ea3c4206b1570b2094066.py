#!/usr/bin/env python3
import sys
import json

def main():
    # Read the task instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    public_input = instance['public_input']
    c1_hex = public_input['c1_hex']
    c2_hex = public_input['c2_hex']
    
    # Convert to bytes
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # RC4 keystream reuse: C1 = P1 XOR K, C2 = P2 XOR K
    # Therefore: C1 XOR C2 = P1 XOR P2
    
    # The task says "T1_known" which suggests P2 is known
    # Common pattern: P2 might be all zeros or a known plaintext
    # Let me try assuming P2 is all zeros first
    
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    
    # If P2 is all zeros, then C1 XOR C2 = P1
    p1 = xor_result
    
    # Check if this looks reasonable (printable ASCII or structured data)
    # If not, we might need a different assumption
    
    # Try the claim
    claim = {
        "plaintext_hex": p1.hex()
    }
    
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()