import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_hex = kp['data']
        plaintext_bytes = bytes.fromhex(plaintext_hex)
        
        # Get corresponding ciphertext bytes
        ciphertext = ct_bytes[msg_idx]
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            c_byte = ciphertext[pos]
            k_byte = p_byte ^ c_byte
            keystream[pos] = k_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ct_bytes[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: plaintext = ciphertext XOR keystream
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # We don't have this keystream byte - this shouldn't happen
            # with a valid instance, but handle it gracefully
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
