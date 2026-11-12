import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = []
    for ct_obj in instance['ciphertexts']:
        ct_data = base64.b64decode(ct_obj['data'])
        ciphertexts.append(ct_data)
    
    # Recover keystream from known plaintexts
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        
        ciphertext = ciphertexts[msg_idx]
        
        # XOR plaintext with ciphertext to get keystream
        for i, pt_byte in enumerate(plaintext):
            pos = offset + i
            ct_byte = ciphertext[pos]
            ks_byte = pt_byte ^ ct_byte
            
            # Store keystream byte
            if pos in keystream:
                # Verify consistency
                if keystream[pos] != ks_byte:
                    # This shouldn't happen if it's the same keystream
                    pass
            keystream[pos] = ks_byte
    
    # Decrypt target
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertexts[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Missing keystream byte - shouldn't happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {
        "plaintext": plaintext_hex
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
