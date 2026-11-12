#!/usr/bin/env python3
import sys
import json
import time

def main():
    start_ns = time.monotonic_ns()
    
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        task = json.load(f)
    
    c1_hex = task['public_input']['c1_hex']
    c2_hex = task['public_input']['c2_hex']
    
    # Convert to bytes
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # RC4 keystream reuse attack:
    # C1 = P1 XOR K
    # C2 = P2 XOR K
    # Therefore: C1 XOR C2 = P1 XOR P2
    
    # Common English text characteristics:
    # - Most common: space (0x20), letters a-z, A-Z
    # - P2 is likely readable English text
    
    # Strategy: assume P2 contains spaces and solve for P1
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    
    # Try assuming each position in P2 is a space (0x20)
    # If P2[i] = 0x20, then P1[i] = xor_result[i] ^ 0x20
    
    # Start with the assumption that spaces are frequent in P2
    p1_candidate = bytearray(64)
    
    for i in range(64):
        # Assume P2[i] is space
        p1_candidate[i] = xor_result[i] ^ 0x20
    
    # Refine: look for patterns
    # Check if result looks like text
    def is_printable_ascii(b):
        return 32 <= b <= 126
    
    # Better approach: frequency analysis
    # Most common character in English is space
    # Try to identify which bytes in xor_result correspond to space in P2
    
    # Alternative: assume P2 is readable text and use heuristics
    # If we XOR with space (0x20), printable chars become:
    # 'A'-'Z' (0x41-0x5A) -> 0x61-0x7A ('a'-'z')
    # 'a'-'z' (0x61-0x7A) -> 0x41-0x5A ('A'-'Z')
    
    # Better strategy: assume both are English text with spaces
    # Use crib-dragging: assume common words
    
    # Most robust: assume P2 has " the " and try positions
    common_phrases = [
        b" the ",
        b"the ",
        b" and ",
        b" of ",
        b" to ",
        b" in ",
        b" is ",
        b" that ",
    ]
    
    # Score each position by trying common phrases
    best_p1 = None
    best_score = -1
    
    for phrase in common_phrases:
        for start_pos in range(len(xor_result) - len(phrase) + 1):
            # Assume P2[start_pos:start_pos+len(phrase)] = phrase
            p1_test = bytearray(64)
            
            # Fill in the known part
            for i in range(len(phrase)):
                p1_test[start_pos + i] = xor_result[start_pos + i] ^ phrase[i]
            
            # For remaining positions, assume space in P2
            for i in range(64):
                if i < start_pos or i >= start_pos + len(phrase):
                    p1_test[i] = xor_result[i] ^ 0x20
            
            # Score: count printable ASCII
            score = sum(1 for b in p1_test if is_printable_ascii(b))
            
            if score > best_score:
                best_score = score
                best_p1 = bytes(p1_test)
    
    # If no good match, fall back to space assumption
    if best_p1 is None:
        best_p1 = bytes(xor_result[i] ^ 0x20 for i in range(64))
    
    end_ns = time.monotonic_ns()
    
    # Output claim
    claim = {"plaintext_hex": best_p1.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()