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
    
    # RC4 keystream reuse: C1 = P1 XOR K, C2 = P2 XOR K
    # Therefore: C1 XOR C2 = P1 XOR P2
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    
    def is_printable(b):
        return 32 <= b <= 126
    
    # More sophisticated crib-dragging attack
    # Try common English phrases in P2 to recover parts of P1
    common_cribs = [
        b"the ", b" the ", b"and ", b" and ", b"that ", b" that ",
        b"with ", b" with ", b"this ", b" this ", b"from ", b" from ",
        b"have ", b" have ", b"will ", b" will ", b"your ", b" your ",
        b"more ", b" more ", b"when ", b" when ", b"which ", b" which ",
        b"their ", b" their ", b"would ", b" would ", b"there ", b" there ",
        b"about ", b" about ", b"could ", b" could ", b"these ", b" these ",
    ]
    
    # Build P1 incrementally
    p1 = bytearray([0] * 64)
    confidence = [0] * 64  # confidence score for each position
    
    # Try each crib at each position in P2
    for crib in common_cribs:
        for pos in range(len(xor_result) - len(crib) + 1):
            # Assume P2[pos:pos+len(crib)] = crib
            # Then P1[pos:pos+len(crib)] = xor_result[pos:pos+len(crib)] XOR crib
            p1_fragment = bytes(xor_result[pos + i] ^ crib[i] for i in range(len(crib)))
            
            # Check if this produces reasonable text in P1
            if all(is_printable(b) for b in p1_fragment):
                # Update P1 with higher confidence
                for i in range(len(crib)):
                    if confidence[pos + i] < len(crib):
                        p1[pos + i] = p1_fragment[i]
                        confidence[pos + i] = len(crib)
    
    # For positions with zero confidence, try space in P2
    for i in range(64):
        if confidence[i] == 0:
            p1[i] = xor_result[i] ^ 0x20
    
    # Second pass: look for common single characters
    # Space is most common (0x20)
    # Try to identify spaces in P2 by checking if P1 result is letter
    for i in range(64):
        test_char = xor_result[i] ^ 0x20
        # If XORing with space gives a letter, likely P2[i] is space
        if (ord('a') <= test_char <= ord('z')) or (ord('A') <= test_char <= ord('Z')):
            if confidence[i] < 2:
                p1[i] = test_char
                confidence[i] = 2
    
    # Third pass: statistical approach
    # The most frequent byte in xor_result likely corresponds to space XOR space = 0
    # or common_char XOR common_char
    
    # Actually, let's try a different angle:
    # Assume both P1 and P2 are English text
    # Most common byte in English text is space (0x20)
    
    # Try assuming different bytes in xor_result correspond to (space, X) pairs
    byte_freq = {}
    for b in xor_result:
        byte_freq[b] = byte_freq.get(b, 0) + 1
    
    # Most frequent XOR values likely involve space
    most_common = sorted(byte_freq.items(), key=lambda x: x[1], reverse=True)
    
    # The most common XOR byte is likely 'X' ^ ' ' where X is a common char
    # If P2 has many spaces, P1 = xor_result ^ 0x20
    # But we already tried that. Let's try: P1 has many spaces instead
    
    p1_alt = bytearray(64)
    for i in range(64):
        # Try: P1[i] = space, so P2[i] = xor_result[i] ^ 0x20
        p2_char = xor_result[i] ^ 0x20
        if is_printable(p2_char):
            p1_alt[i] = 0x20
        else:
            # Fall back to assuming P2[i] = space
            p1_alt[i] = xor_result[i] ^ 0x20
    
    # Choose the result with more printable characters
    score1 = sum(1 for b in p1 if is_printable(b))
    score2 = sum(1 for b in p1_alt if is_printable(b))
    
    if score2 > score1:
        p1 = p1_alt
    
    end_ns = time.monotonic_ns()
    
    claim = {"plaintext_hex": p1.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()