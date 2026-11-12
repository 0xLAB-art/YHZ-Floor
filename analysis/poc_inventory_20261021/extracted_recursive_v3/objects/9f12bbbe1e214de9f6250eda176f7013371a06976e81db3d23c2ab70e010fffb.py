import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ciphertext_bytes = {}
    for ct in ciphertexts:
        idx = ct['message_index']
        ciphertext_bytes[idx] = bytes.fromhex(ct['data'])
    
    # Recover keystream from known plaintexts
    # keystream[position] = ciphertext[position] ^ plaintext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_data = bytes.fromhex(kp['data'])
        
        ciphertext = ciphertext_bytes[msg_idx]
        
        # Recover keystream at these positions
        for i, pt_byte in enumerate(plaintext_data):
            pos = offset + i
            ct_byte = ciphertext[pos]
            keystream[pos] = ct_byte ^ pt_byte
    
    # Now decrypt the target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_bytes[target_msg_idx]
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: plaintext = ciphertext ^ keystream
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Should not happen if we have enough known plaintexts
            plaintext.append(0)
    
    plaintext_hex = bytes(plaintext).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
