import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append({
            'data': bytes.fromhex(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Convert known plaintexts to bytes
    kp_bytes = []
    for kp in known_plaintexts:
        kp_bytes.append({
            'data': bytes.fromhex(kp['data']),
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    # This is a many-time pad attack
    # XOR property: C1 XOR C2 = (P1 XOR K) XOR (P2 XOR K) = P1 XOR P2
    # If we know P1, we can recover P2
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Build the keystream for the target range
    keystream = [None] * target_length
    
    # For each known plaintext, we can recover the keystream
    for kp in kp_bytes:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = kp['data']
        
        # Get the corresponding ciphertext
        ct = next(c['data'] for c in ct_bytes if c['message_index'] == msg_idx)
        
        # Recover keystream: K = P XOR C
        for i, pt_byte in enumerate(pt_data):
            key_pos = offset + i
            if target_offset <= key_pos < target_offset + target_length:
                target_pos = key_pos - target_offset
                ct_byte = ct[key_pos]
                keystream[target_pos] = pt_byte ^ ct_byte
    
    # Now use the keystream to decrypt the target
    target_ct = next(c['data'] for c in ct_bytes if c['message_index'] == target_msg_idx)
    
    plaintext = []
    for i in range(target_length):
        if keystream[i] is not None:
            pt_byte = target_ct[target_offset + i] ^ keystream[i]
            plaintext.append(pt_byte)
        else:
            # Try to recover using XOR relationships between ciphertexts and known plaintexts
            # For position target_offset + i in target message
            # We need to find another message where we know the plaintext at this position
            
            found = False
            for kp in kp_bytes:
                if kp['offset'] <= target_offset + i < kp['offset'] + len(kp['data']):
                    # This known plaintext covers this position
                    other_msg_idx = kp['message_index']
                    other_offset = kp['offset']
                    other_pt_byte = kp['data'][target_offset + i - other_offset]
                    
                    # Get ciphertexts
                    other_ct = next(c['data'] for c in ct_bytes if c['message_index'] == other_msg_idx)
                    
                    # C_target XOR C_other = P_target XOR P_other
                    # P_target = (C_target XOR C_other) XOR P_other
                    ct_xor = target_ct[target_offset + i] ^ other_ct[target_offset + i]
                    pt_byte = ct_xor ^ other_pt_byte
                    plaintext.append(pt_byte)
                    found = True
                    break
            
            if not found:
                # Should not happen if puzzle is solvable
                plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
