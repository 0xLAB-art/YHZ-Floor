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
    
    # XOR the two ciphertexts to get P1 ⊕ P2
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    
    # T1_known suggests P2 is a known plaintext
    # Common patterns: all zeros, ASCII text, repeated pattern
    # Let's try assuming P2 is all zeros first
    p2_candidate = bytes(64)  # 64 zero bytes
    p1 = bytes(a ^ b for a, b in zip(xor_result, p2_candidate))
    
    # Check if P1 looks reasonable (printable ASCII or structured data)
    if all(32 <= b < 127 or b in (9, 10, 13) for b in p1):
        claim = {"plaintext_hex": p1.hex()}
        print(f"CLAIM:{json.dumps(claim)}")
        return
    
    # Try P2 as repeated "TEST" pattern
    p2_candidate = (b"TEST" * 16)[:64]
    p1 = bytes(a ^ b for a, b in zip(xor_result, p2_candidate))
    if all(32 <= b < 127 or b in (9, 10, 13) for b in p1):
        claim = {"plaintext_hex": p1.hex()}
        print(f"CLAIM:{json.dumps(claim)}")
        return
    
    # Try P2 as sequential bytes 0x00 to 0x3f
    p2_candidate = bytes(range(64))
    p1 = bytes(a ^ b for a, b in zip(xor_result, p2_candidate))
    if all(32 <= b < 127 or b in (9, 10, 13) for b in p1):
        claim = {"plaintext_hex": p1.hex()}
        print(f"CLAIM:{json.dumps(claim)}")
        return
    
    # Try P2 as all 0x01
    p2_candidate = bytes([1] * 64)
    p1 = bytes(a ^ b for a, b in zip(xor_result, p2_candidate))
    
    claim = {"plaintext_hex": p1.hex()}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == '__main__':
    main()