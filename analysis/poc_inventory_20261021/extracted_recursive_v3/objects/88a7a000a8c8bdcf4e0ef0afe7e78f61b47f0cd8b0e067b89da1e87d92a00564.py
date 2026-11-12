import base64
import json
import sys

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({'data': data, 'message_index': ct['message_index']})
    
    # Build a map from message_index to ciphertext data
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = ct['data']
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        if msg_idx not in ct_map:
            continue
            
        ciphertext = ct_map[msg_idx]
        
        # XOR ciphertext with known plaintext to get keystream
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                k_byte = ciphertext[pos] ^ p_byte
                
                # Store keystream byte (verify consistency if already exists)
                if pos in keystream:
                    if keystream[pos] != k_byte:
                        # Inconsistency - shouldn't happen with correct data
                        pass
                else:
                    keystream[pos] = k_byte
    
    # Decrypt target
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_map:
        print(json.dumps({"plaintext": "00" * target_length}))
        return
    
    target_ciphertext = ct_map[target_msg_idx]
    
    # Decrypt using recovered keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # Missing keystream byte - shouldn't happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == '__main__':
    main()