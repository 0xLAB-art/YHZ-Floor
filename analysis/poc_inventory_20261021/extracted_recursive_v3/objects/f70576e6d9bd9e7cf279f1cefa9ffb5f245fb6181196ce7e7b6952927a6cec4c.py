import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ciphertext_data = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ciphertext_data[msg_idx] = bytes.fromhex(ct['data'])
    
    # Recover keystream bytes using known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_hex = kp['data']
        plaintext_bytes = bytes.fromhex(plaintext_hex)
        
        # Get corresponding ciphertext
        ciphertext = ciphertext_data[msg_idx]
        
        # Recover keystream: K = C ⊕ P
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = c_byte ^ p_byte
                keystream[pos] = k_byte
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_data[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            c_byte = target_ciphertext[pos]
            k_byte = keystream[pos]
            p_byte = c_byte ^ k_byte
            plaintext_bytes.append(p_byte)
        else:
            # Should not happen if we have complete keystream coverage
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()