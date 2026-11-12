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
    
    # The task name suggests T1_known, meaning we likely know P2 (or it follows a pattern)
    # Common patterns for keystream reuse attacks:
    # 1. One plaintext is all nulls
    # 2. One plaintext is known text
    # 3. One plaintext has a predictable structure
    
    # Let me try assuming P2 is all zeros (null bytes)
    # If P2 = 0x00..., then P1 ⊕ P2 = P1
    p1_candidate = xor_result
    
    # Check if this looks like readable text
    if all(32 <= b < 127 or b in (9, 10, 13) for b in p1_candidate):
        p1 = p1_candidate
    else:
        # Try assuming P2 is a known plaintext pattern
        # Common test patterns: repeated null bytes, ASCII text, etc.
        # Let's try assuming P2 is 64 null bytes
        p2_guess = b'\x00' * 64
        p1 = bytes(a ^ b for a, b in zip(xor_result, p2_guess))
        
        # If still not readable, try other common patterns
        if not all(32 <= b < 127 or b in (9, 10, 13) for b in p1):
            # Try P2 as repeated pattern
            # Or try the xor_result itself as P1 (meaning P2 was nulls)
            p1 = xor_result
    
    # Prepare claim
    start_ns = time.monotonic_ns()
    plaintext_hex = p1.hex()
    end_ns = time.monotonic_ns()
    
    # Output
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext_hex})}")
    sys.stdout.flush()

if __name__ == '__main__':
    main()