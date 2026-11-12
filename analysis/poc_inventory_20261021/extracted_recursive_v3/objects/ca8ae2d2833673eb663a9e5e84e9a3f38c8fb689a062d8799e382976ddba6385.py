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
    
    # Build keystream from known plaintexts
    # For stream cipher: ciphertext XOR plaintext = keystream
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = bytes.fromhex(kp['data'])
        
        ciphertext = ct_bytes[msg_idx]
        
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            c_byte = ciphertext[pos]
            k_byte = c_byte ^ p_byte
            keystream[pos] = k_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            c_byte = target_ct[pos]
            k_byte = keystream[pos]
            p_byte = c_byte ^ k_byte
            plaintext_bytes.append(p_byte)
        else:
            # Should not happen if keystream is complete
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()