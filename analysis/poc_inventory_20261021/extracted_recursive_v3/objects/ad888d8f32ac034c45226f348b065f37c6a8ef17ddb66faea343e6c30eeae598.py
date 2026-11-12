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
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # XOR the two ciphertexts to get P1 ⊕ P2
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    
    # T1_known suggests plaintext 1 is known
    # Common known plaintexts in crypto challenges:
    # - All zeros
    # - "A" * 64 or other repeated characters
    # - Known message formats
    
    # Try common patterns
    candidates = [
        b'\x00' * 64,  # All zeros
        b'A' * 64,
        b'The secret message is: ' + b'\x00' * 40,
        b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + b'\x00' * 32,
    ]
    
    # If P1 is known, then P2 = (P1 ⊕ P2) ⊕ P1
    # But we want P1, so if P2 is known: P1 = (P1 ⊕ P2) ⊕ P2
    
    # Actually, let's think about this differently.
    # The task asks for P1. If "T1_known" means we should know what T1 is,
    # perhaps T1 refers to one of the texts and we need to figure out which is known.
    
    # Let me try assuming P2 is a known plaintext and recover P1
    # Common known plaintext: all zeros or a flag format
    
    # Try P2 = all zeros -> P1 = xor_result
    p1_candidate = xor_result
    
    # Check if it looks reasonable (printable ASCII)
    if all(32 <= b < 127 or b in (9, 10, 13) for b in p1_candidate):
        claim = {"plaintext_hex": p1_candidate.hex()}
        print(f"CLAIM:{json.dumps(claim)}")
        return
    
    # Try other known P2 patterns
    for known_p2 in candidates:
        p1_candidate = bytes(a ^ b for a, b in zip(xor_result, known_p2))
        if all(32 <= b < 127 or b in (9, 10, 13) for b in p1_candidate):
            claim = {"plaintext_hex": p1_candidate.hex()}
            print(f"CLAIM:{json.dumps(claim)}")
            return
    
    # If nothing works, just try the XOR result itself
    claim = {"plaintext_hex": xor_result.hex()}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == '__main__':
    main()