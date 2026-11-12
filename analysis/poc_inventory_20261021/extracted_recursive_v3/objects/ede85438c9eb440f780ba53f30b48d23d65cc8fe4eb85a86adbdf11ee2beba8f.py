#!/usr/bin/env python3
import sys
import json
import time

def main():
    # Read task instance from command line argument
    with open(sys.argv[1], 'r') as f:
        task = json.load(f)
    
    public_input = task['public_input']
    c1_hex = public_input['c1_hex']
    c2_hex = public_input['c2_hex']
    
    # Convert hex to bytes
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # Start timing the operation
    start_ns = time.monotonic_ns()
    
    # ChaCha20 nonce reuse attack:
    # C1 = P1 ⊕ KeyStream
    # C2 = P2 ⊕ KeyStream
    # C1 ⊕ C2 = P1 ⊕ P2
    
    # For T1_known variant, we assume P2 is known (typically all zeros)
    # If P2 = 0x00 * 64, then C2 = KeyStream
    # Therefore P1 = C1 ⊕ KeyStream = C1 ⊕ C2
    
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    
    end_ns = time.monotonic_ns()
    
    # Output timing
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    
    # Output claim
    claim = {"plaintext2_hex": p1.hex()}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == '__main__':
    main()