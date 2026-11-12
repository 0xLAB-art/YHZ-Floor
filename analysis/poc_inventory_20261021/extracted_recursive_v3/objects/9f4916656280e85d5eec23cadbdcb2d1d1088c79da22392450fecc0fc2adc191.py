import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Decode all ciphertexts
    decoded_ciphertexts = {}
    for ct in ciphertexts:
        decoded_ciphertexts[ct['message_index']] = base64.b64decode(ct['data'])
    
    # Decode all known plaintexts
    known_data = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        if msg_idx not in known_data:
            known_data[msg_idx] = {}
        for i, byte in enumerate(plaintext):
            known_data[msg_idx][offset + i] = byte
    
    # Extract keystream bytes from known plaintexts
    keystream = {}
    for msg_idx in known_data:
        ciphertext = decoded_ciphertexts[msg_idx]
        for offset, plain_byte in known_data[msg_idx].items():
            cipher_byte = ciphertext[offset]
            key_byte = cipher_byte ^ plain_byte
            if offset not in keystream:
                keystream[offset] = key_byte
            elif keystream[offset] != key_byte:
                # Inconsistency detected - stream cipher reuse issue
                pass
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = decoded_ciphertexts[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            plain_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(plain_byte)
        else:
            # Should not happen if keystream is complete
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()