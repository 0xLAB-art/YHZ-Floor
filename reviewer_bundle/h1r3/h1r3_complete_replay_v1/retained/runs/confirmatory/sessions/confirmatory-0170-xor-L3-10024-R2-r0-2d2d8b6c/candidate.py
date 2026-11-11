import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(base64.b64decode(ct['data']))
    
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
    
    # This is a stream cipher reuse attack
    # C_i = P_i XOR K where K is the keystream
    # If we know P_i at position j, we can recover K[j] = C_i[j] XOR P_i[j]
    # Then we can decrypt any other ciphertext at position j: P_k[j] = C_k[j] XOR K[j]
    
    # Find the maximum position we need
    max_pos = target_offset + target_length
    
    # Recover keystream
    keystream = [None] * max_pos
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        ct = ciphertexts[msg_idx]
        
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct):
                # Recover keystream byte
                k_byte = ct[pos] ^ p_byte
                keystream[pos] = k_byte
    
    # Decrypt target
    target_ct = ciphertexts[target_msg_idx]
    result = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            plaintext_byte = target_ct[pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen if the problem is well-formed
            result.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(result).hex()
    
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
