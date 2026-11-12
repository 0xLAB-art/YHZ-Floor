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
    ciphertext_bytes = []
    for ct in ciphertexts:
        ciphertext_bytes.append(bytes.fromhex(ct['data']))
    
    # Recover keystream bytes using known plaintexts
    # keystream[offset] = ciphertext[message_index][offset] ^ plaintext[offset]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = bytes.fromhex(kp['data'])
        
        ciphertext = ciphertext_bytes[msg_idx]
        
        # Recover keystream bytes at these offsets
        for i, pt_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                key_byte = ciphertext[pos] ^ pt_byte
                keystream[pos] = key_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen if the challenge is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
