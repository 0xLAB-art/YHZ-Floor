import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append(data)
    
    # Find the maximum length to determine keystream size needed
    max_len = max(len(ct) for ct in ciphertexts)
    
    # Recover keystream using known plaintexts
    # keystream[i] = plaintext[i] XOR ciphertext[i]
    keystream = [None] * max_len
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        ciphertext = ciphertexts[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                # Recover keystream byte
                ks_byte = pt_byte ^ ciphertext[pos]
                
                # Store or verify consistency
                if keystream[pos] is None:
                    keystream[pos] = ks_byte
                elif keystream[pos] != ks_byte:
                    # Inconsistency - shouldn't happen if it's a proper many-time pad
                    pass
    
    # Now decrypt the target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    target_ciphertext = ciphertexts[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            # Decrypt: plaintext = ciphertext XOR keystream
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen if the challenge is solvable
            plaintext_bytes.append(0)
    
    # Convert to lowercase hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()