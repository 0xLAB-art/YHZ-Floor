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
    
    # RC4 keystream reuse attack:
    # C1 = P1 ⊕ K
    # C2 = P2 ⊕ K
    # C1 ⊕ C2 = P1 ⊕ P2
    
    # The task name includes "T1_known" which suggests P2 is known
    # Common scenario: P2 is a known plaintext (often all zeros or a standard message)
    
    # Try common known plaintexts:
    # 1. All zeros
    # 2. Common ASCII patterns
    # 3. Standard messages
    
    start_ns = time.monotonic_ns()
    
    # If P2 is all zeros: P1 = C1 ⊕ C2 ⊕ P2 = C1 ⊕ C2 ⊕ 0 = C1 ⊕ C2
    # But that doesn't match the attack model
    
    # More likely: C1 ⊕ C2 = P1 ⊕ P2
    # If we know P2, then P1 = (C1 ⊕ C2) ⊕ P2
    
    # For "T1_known", the convention is that the first plaintext P1 is what we're recovering
    # and we have some known relationship or known second plaintext
    
    # Common attack: P2 is a known string, often all zeros for testing
    # Let's try: if C2 encrypts all zeros, then C2 = K (the keystream)
    # Therefore P1 = C1 ⊕ K = C1 ⊕ C2
    
    p1_candidate = bytes(c1[i] ^ c2[i] for i in range(len(c1)))
    
    end_ns = time.monotonic_ns()
    
    # Output result
    plaintext_hex = p1_candidate.hex()
    
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext_hex})}")
    print(f"OPSPAN_NS:{end_ns - start_ns}")

if __name__ == '__main__':
    main()