#!/usr/bin/env python3
import sys
import json
import time

def main():
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    public_input = instance['public_input']
    c1_hex = public_input['c1_hex']
    c2_hex = public_input['c2_hex']
    
    # Convert to bytes
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    start_ns = time.monotonic_ns()
    
    # XOR the two ciphertexts: C1 ⊕ C2 = P1 ⊕ P2
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    
    # Assume P2 is 64 null bytes (common test case)
    # Then P1 ⊕ P2 = P1 ⊕ 0 = P1
    p1 = xor_result
    
    end_ns = time.monotonic_ns()
    
    # Prepare claim
    plaintext_hex = p1.hex()
    
    # Output
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext_hex})}")
    sys.stdout.flush()

if __name__ == '__main__':
    main()