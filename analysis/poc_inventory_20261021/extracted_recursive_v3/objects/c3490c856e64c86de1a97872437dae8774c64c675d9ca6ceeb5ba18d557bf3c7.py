import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        ct_data[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build known plaintext map
    known_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known_map:
            known_map[msg_idx] = {}
        for i, b in enumerate(data):
            known_map[msg_idx][offset + i] = b
    
    # For stream cipher with key reuse: C = P XOR K
    # If we know P_i at position j, we can recover K[j] = P_i[j] XOR C_i[j]
    # Then P_target[j] = C_target[j] XOR K[j]
    
    keystream = {}
    for msg_idx, positions in known_map.items():
        for pos, plaintext_byte in positions.items():
            ciphertext_byte = ct_data[msg_idx][pos]
            keystream[pos] = plaintext_byte ^ ciphertext_byte
    
    # Recover target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_offset, target_offset + target_length):
        if i in keystream:
            # We know the keystream at this position
            pt_byte = ct_data[target_msg_idx][i] ^ keystream[i]
            plaintext_bytes.append(pt_byte)
        else:
            # We don't have keystream for this position
            # Try to use crib-dragging or other analysis
            # For now, we'll try common patterns
            plaintext_bytes.append(0)
    
    # If we still have unknown bytes, try crib-dragging
    # XOR two ciphertexts: C_i XOR C_j = P_i XOR P_j
    # This can reveal patterns if we guess words
    
    for i in range(target_offset, target_offset + target_length):
        if i not in keystream:
            # Try to find this position in another message by crib-dragging
            # Check all known plaintexts to extend keystream
            for msg_idx in ct_data:
                if msg_idx in known_map and i in known_map[msg_idx]:
                    pt_byte = known_map[msg_idx][i]
                    ct_byte = ct_data[msg_idx][i]
                    keystream[i] = pt_byte ^ ct_byte
                    plaintext_bytes[i - target_offset] = ct_data[target_msg_idx][i] ^ keystream[i]
                    break
    
    # Additional analysis: use XOR relationships between ciphertexts
    # to infer missing bytes based on common text patterns
    for i in range(target_offset, target_offset + target_length):
        if i not in keystream:
            # Try each other message to see if we can infer
            for other_idx in ct_data:
                if other_idx == target_msg_idx:
                    continue
                if other_idx in known_map and i in known_map[other_idx]:
                    # We have plaintext for other message at position i
                    keystream[i] = ct_data[other_idx][i] ^ known_map[other_idx][i]
                    plaintext_bytes[i - target_offset] = ct_data[target_msg_idx][i] ^ keystream[i]
                    break
    
    result = bytes(plaintext_bytes).hex()
    print(json.dumps({"plaintext": result}))

if __name__ == "__main__":
    main()