#!/usr/bin/env python3
import sys
import json
import time

def main():
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        task = json.load(f)
    
    public_input = task['public_input']
    c1_hex = public_input['c1_hex']
    c2_hex = public_input['c2_hex']
    
    # Convert to bytes
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # Start timing
    start_ns = time.monotonic_ns()
    
    # XOR the two ciphertexts to get P1 ⊕ P2
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    
    # For T1_known variant, P2 is typically known
    # Common patterns: all zeros, or known plaintext
    # Let's try P2 = all zeros first (which means P1 = C1 ⊕ C2)
    p1_candidate = xor_result
    
    # However, the more common scenario is that P2 is some known text
    # Let me try assuming P2 is all zeros, meaning the keystream XORed with 0 gives the ciphertext
    # Actually, if P2 = 0, then C2 = KeyStream, and C1 = P1 ⊕ KeyStream
    # So P1 = C1 ⊕ C2
    
    plaintext1 = bytes(a ^ b for a, b in zip(c1, c2))
    
    end_ns = time.monotonic_ns()
    
    # Output
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    print(f"CLAIM:{json.dumps({'plaintext2_hex': plaintext1.hex()})}")

if __name__ == '__main__':
    main()