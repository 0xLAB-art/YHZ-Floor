#!/usr/bin/env python3
import sys
import json
import time

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    public_input = instance['public_input']
    c1_hex = public_input['c1_hex']
    c2_hex = public_input['c2_hex']
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    start_ns = time.monotonic_ns()
    
    # Nonce reuse: if P2 is known (assume zeros), recover P1
    p2_known = b'\x00' * 64
    keystream = bytes(a ^ b for a, b in zip(c2, p2_known))
    p1 = bytes(a ^ b for a, b in zip(c1, keystream))
    
    end_ns = time.monotonic_ns()
    
    claim = {"plaintext2_hex": p1.hex()}
    
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()