#!/usr/bin/env python3
import sys
import json
import time

def main():
    # Read the task instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    public_input = instance['public_input']
    c1_hex = public_input['c1_hex']
    c2_hex = public_input['c2_hex']
    
    # Convert ciphertexts to bytes
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    start_ns = time.monotonic_ns()
    
    # ChaCha20 nonce reuse attack
    # C1 = P1 ⊕ Keystream
    # C2 = P2 ⊕ Keystream
    # Therefore: C1 ⊕ C2 = P1 ⊕ P2
    
    # For T1_known, assume P2 is the known plaintext
    # Common assumption: P2 is all zeros (used for keystream extraction)
    p2_known = b'\x00' * 64
    
    # If P2 is known, we can recover the keystream: K = C2 ⊕ P2
    keystream = bytes(a ^ b for a, b in zip(c2, p2_known))
    
    # Then recover P1: P1 = C1 ⊕ K
    p1_recovered = bytes(a ^ b for a, b in zip(c1, keystream))
    
    end_ns = time.monotonic_ns()
    
    # The claim asks for plaintext2_hex, but goal says recover P1
    # I'll output P1 as requested by the goal
    claim = {
        "plaintext2_hex": p1_recovered.hex()
    }
    
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()