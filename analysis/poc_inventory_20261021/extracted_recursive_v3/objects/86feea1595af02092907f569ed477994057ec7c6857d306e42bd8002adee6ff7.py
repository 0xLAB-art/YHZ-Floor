#!/usr/bin/env python3
import sys
import json

def main():
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    public_input = instance['public_input']
    c1_hex = public_input['c1_hex']
    c2_hex = public_input['c2_hex']
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # XOR the two ciphertexts: C1 ⊕ C2 = (P1 ⊕ K) ⊕ (P2 ⊕ K) = P1 ⊕ P2
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    
    # T1_known likely means P2 is a known plaintext
    # Try P2 = all zeros, which means P1 = P1 ⊕ P2 = xor_result
    p1 = xor_result
    
    claim = {"plaintext_hex": p1.hex()}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == '__main__':
    main()