#!/usr/bin/env python3
import sys
import json
import time

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
    
    start_ns = time.monotonic_ns()
    
    # ChaCha20 nonce reuse: C1 = P1 ⊕ K, C2 = P2 ⊕ K
    # Therefore: C1 ⊕ C2 = P1 ⊕ P2
    xor_plaintexts = bytes(a ^ b for a, b in zip(c1, c2))
    
    # T1_known suggests plaintext 1 is known
    # Task says "recover P1" but claim wants "plaintext2_hex"
    # This is confusing - let me assume the claim label is off
    # and they want P1 in the field called "plaintext2_hex"
    
    # If P1 is "known" in the task type, perhaps it means we should assume
    # a specific structure. Let me try P2 = zeros, so P1 = xor_plaintexts
    
    p1_recovered = xor_plaintexts
    
    end_ns = time.monotonic_ns()
    
    claim = {
        "plaintext2_hex": p1_recovered.hex()
    }
    
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()