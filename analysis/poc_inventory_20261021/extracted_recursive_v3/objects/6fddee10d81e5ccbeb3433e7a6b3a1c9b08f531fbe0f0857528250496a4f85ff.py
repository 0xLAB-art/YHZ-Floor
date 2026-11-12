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
    
    # XOR the ciphertexts to get P1 XOR P2
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    
    # In a typical ChaCha20 nonce reuse attack with "T1_known",
    # we might have a known plaintext. Common scenarios:
    # - P2 is known (e.g., "This is a secret message..." format)
    # - P1 or P2 has predictable structure
    
    # Let's try assuming P2 is printable ASCII or has a known prefix
    # If P2 is known, then P1 = P2 XOR (C1 XOR C2)
    
    # Try common known plaintext patterns
    # Pattern 1: "This is a secret message" or similar
    known_prefix = b"The secret message is: "
    
    # If we assume P2 starts with this prefix:
    # P1[:len(prefix)] = known_prefix XOR xor_result[:len(prefix)]
    potential_p1_prefix = bytes(a ^ b for a, b in zip(known_prefix[:min(len(known_prefix), len(xor_result))], xor_result[:min(len(known_prefix), len(xor_result))]))
    
    # Check if this looks like readable text
    # Actually, let me try a different approach: assume P2 is all printable ASCII
    # and solve for P1 character by character
    
    # Better approach: Try to identify if one plaintext has structure
    # by testing if XORing with common strings produces readable text
    
    # Common patterns in CTF challenges:
    test_patterns = [
        b"The secret key is: ",
        b"Flag: ",
        b"Message: ",
        b"Plaintext 2: ",
        b"This is message 2",
        b"AAAAAAAAAAAAAAAA",  # Sometimes padding
        b"\x00" * 64,  # Zero plaintext
    ]
    
    best_p1 = None
    best_score = 0
    
    for pattern in test_patterns:
        # Extend or truncate pattern to match length
        if len(pattern) < len(xor_result):
            # Try this pattern at the start and pad rest
            p2_test = pattern + bytes(len(xor_result) - len(pattern))
            p1_candidate = bytes(a ^ b for a, b in zip(p2_test, xor_result))
            
            # Score based on printable ASCII characters
            score = sum(1 for b in p1_candidate if 32 <= b <= 126)
            if score > best_score:
                best_score = score
                best_p1 = p1_candidate
    
    # If no pattern worked well, try assuming P2 is all spaces or zeros
    # P2 = all spaces (0x20)
    p2_spaces = bytes([0x20] * len(xor_result))
    p1_from_spaces = bytes(a ^ b for a, b in zip(p2_spaces, xor_result))
    score_spaces = sum(1 for b in p1_from_spaces if 32 <= b <= 126)
    
    if score_spaces > best_score:
        best_p1 = p1_from_spaces
        best_score = score_spaces
    
    # Final fallback: just return XOR result as P1 (assuming P2 is zeros)
    if best_p1 is None:
        best_p1 = xor_result
    
    # Output claim
    claim = {
        "plaintext2_hex": best_p1.hex()
    }
    
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()