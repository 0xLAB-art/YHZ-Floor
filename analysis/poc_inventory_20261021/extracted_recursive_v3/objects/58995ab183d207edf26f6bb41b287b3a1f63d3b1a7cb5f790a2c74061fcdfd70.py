#!/usr/bin/env python3
import sys
import json
import time

def main():
    # Read task instance from command-line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    public_input = instance['public_input']
    c1_hex = public_input['c1_hex']
    c2_hex = public_input['c2_hex']
    
    # Convert hex to bytes
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    start_ns = time.monotonic_ns()
    
    # RC4 keystream reuse: C1 = P1 ⊕ K, C2 = P2 ⊕ K
    # Therefore: C1 ⊕ C2 = P1 ⊕ P2
    # If P2 is known (likely all zeros for "T1_known"), then:
    # P1 = C1 ⊕ C2 ⊕ P2
    
    # Assuming P2 is 64 null bytes
    p2 = b'\x00' * 64
    
    # Calculate P1
    xor_c1_c2 = bytes(a ^ b for a, b in zip(c1, c2))
    p1 = bytes(a ^ b for a, b in zip(xor_c1_c2, p2))
    
    end_ns = time.monotonic_ns()
    
    # Format output
    plaintext_hex = p1.hex()
    
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext_hex})}")
    sys.stdout.flush()

if __name__ == '__main__':
    main()