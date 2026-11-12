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
    kp_data = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in kp_data:
            kp_data[msg_idx] = {}
        for i, b in enumerate(data):
            kp_data[msg_idx][offset + i] = b
    
    # This is a stream cipher reuse attack
    # C_i = P_i XOR K where K is the keystream
    # If we know P_i at position j, we can recover K[j] = C_i[j] XOR P_i[j]
    # Then we can decrypt any other message at position j: P_k[j] = C_k[j] XOR K[j]
    
    # Recover keystream
    keystream = {}
    for msg_idx, positions in kp_data.items():
        for pos, plaintext_byte in positions.items():
            ciphertext_byte = ct_bytes[msg_idx][pos]
            keystream[pos] = ciphertext_byte ^ plaintext_byte
    
    # Decrypt target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_offset, target_offset + target_length):
        if i in keystream:
            # We know the keystream at this position
            pt_byte = ct_bytes[target_msg_idx][i] ^ keystream[i]
            plaintext.append(pt_byte)
        else:
            # We don't have keystream for this position
            # Try to infer from other messages or use heuristics
            # For now, we'll use 0x00 as placeholder (this shouldn't happen with sufficient data)
            plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
