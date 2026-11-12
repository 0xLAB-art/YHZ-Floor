import json
import sys
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': base64.b64decode(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        known_plaintexts.append({
            'data': base64.b64decode(kp['data']),
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find the target ciphertext
    target_ct = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ct = ct['data']
            break
    
    # This is a many-time pad attack
    # C_i = P_i XOR K where K is the reused key (stream)
    # If we know P_i at position j, we can recover K[j] = C_i[j] XOR P_i[j]
    # Then we can decrypt any other ciphertext at position j: P_x[j] = C_x[j] XOR K[j]
    
    # Recover the keystream
    max_len = max(len(ct['data']) for ct in ciphertexts)
    keystream = [None] * max_len
    
    # Use known plaintexts to recover keystream bytes
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        # Find the corresponding ciphertext
        ct_data = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ct_data = ct['data']
                break
        
        if ct_data:
            # Recover keystream bytes
            for i, p_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ct_data):
                    k_byte = ct_data[pos] ^ p_byte
                    keystream[pos] = k_byte
    
    # Now decrypt the target using the recovered keystream
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            plaintext_byte = target_ct[pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # If we don't have the keystream at this position, we need to infer it
            # This shouldn't happen if we have enough known plaintexts
            result.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(result).hex()
    
    # Output
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
