import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This appears to be a many-time pad attack
    # We have multiple messages encrypted with the same key stream
    # known_plaintexts gives us plaintext at specific positions in specific messages
    
    # Build keystream from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_hex = kp['data']
        plaintext_bytes = bytes.fromhex(plaintext_hex)
        
        # XOR ciphertext with plaintext to get keystream
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ct_bytes[msg_idx][pos]
            key_byte = ct_byte ^ pt_byte
            
            # Store in keystream dict
            if pos not in keystream:
                keystream[pos] = key_byte
            else:
                # Verify consistency
                if keystream[pos] != key_byte:
                    # Conflict - this shouldn't happen in a proper stream cipher reuse
                    pass
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We have the keystream byte, so we can decrypt
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # We don't have this keystream byte
            # We need to derive it somehow or make an educated guess
            # For now, let's try to use crib-dragging or frequency analysis
            plaintext_bytes.append(0)
    
    # Try to fill in missing bytes using crib-dragging across messages
    # For each unknown position, XOR all ciphertexts at that position with common patterns
    
    for i in range(target_length):
        pos = target_offset + i
        if pos not in keystream:
            # Try to deduce keystream from other messages
            # Collect all ciphertext bytes at this position
            ct_at_pos = []
            for j, ct in enumerate(ct_bytes):
                if pos < len(ct):
                    ct_at_pos.append((j, ct[pos]))
            
            # Try common plaintext characters and see if they produce consistent keystream
            # across multiple messages where we have known plaintexts nearby
            
            # For simplicity, try space (0x20) and common ASCII characters
            # and see which gives the most plausible plaintexts in other messages
            
            best_key = None
            best_score = -1
            
            for candidate_key in range(256):
                score = 0
                for msg_idx, ct_byte in ct_at_pos:
                    pt_candidate = ct_byte ^ candidate_key
                    # Score based on printable ASCII and common characters
                    if 32 <= pt_candidate <= 126:
                        score += 1
                    if 97 <= pt_candidate <= 122:  # lowercase
                        score += 2
                    if pt_candidate in [32, 101, 116, 97, 111, 105, 110]:  # space, e, t, a, o, i, n
                        score += 3
                
                if score > best_score:
                    best_score = score
                    best_key = candidate_key
            
            if best_key is not None:
                keystream[pos] = best_key
                plaintext_bytes[i] = target_ct[pos] ^ best_key
    
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
