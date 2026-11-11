import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Convert known plaintexts to bytes
    kp_bytes = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in kp_bytes:
            kp_bytes[msg_idx] = {}
        for i, byte in enumerate(data):
            kp_bytes[msg_idx][offset + i] = byte
    
    # Recover keystream bytes using known plaintexts
    # For stream cipher: ciphertext = plaintext XOR keystream
    # So: keystream = plaintext XOR ciphertext
    keystream = {}
    for msg_idx, positions in kp_bytes.items():
        for pos, pt_byte in positions.items():
            ct_byte = ct_bytes[msg_idx][pos]
            ks_byte = pt_byte ^ ct_byte
            if pos in keystream:
                # Verify consistency
                if keystream[pos] != ks_byte:
                    pass  # Handle inconsistency if needed
            else:
                keystream[pos] = ks_byte
    
    # Recover target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_offset, target_offset + target_length):
        if i in keystream:
            # We know the keystream byte at this position
            ct_byte = ct_bytes[target_msg_idx][i]
            pt_byte = ct_byte ^ keystream[i]
            plaintext.append(pt_byte)
        else:
            # We don't know the keystream at this position
            # Try to deduce it using crib dragging or other techniques
            # For now, we'll attempt a heuristic approach
            
            # Try XORing with other ciphertexts to find patterns
            best_byte = 0
            found = False
            
            # Check if we can deduce from XOR of two ciphertexts
            for other_idx in ct_bytes:
                if other_idx == target_msg_idx:
                    continue
                if other_idx in kp_bytes and i in kp_bytes[other_idx]:
                    # We know plaintext for other message at position i
                    other_pt = kp_bytes[other_idx][i]
                    other_ct = ct_bytes[other_idx][i]
                    ks_byte = other_pt ^ other_ct
                    ct_byte = ct_bytes[target_msg_idx][i]
                    pt_byte = ct_byte ^ ks_byte
                    plaintext.append(pt_byte)
                    found = True
                    break
            
            if not found:
                # Fallback: assume space or common character
                plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()
