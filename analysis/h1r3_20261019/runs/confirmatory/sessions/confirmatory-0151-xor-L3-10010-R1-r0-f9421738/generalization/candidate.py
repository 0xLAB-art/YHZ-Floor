import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a map of ciphertext data by message_index
    ciphertext_map = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        data_hex = ct['data']
        ciphertext_map[msg_idx] = bytes.fromhex(data_hex)
    
    # Recover keystream from known plaintexts
    # keystream[position] = plaintext[position] XOR ciphertext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_hex = kp['data']
        plaintext_bytes = bytes.fromhex(plaintext_hex)
        
        if msg_idx in ciphertext_map:
            ciphertext = ciphertext_map[msg_idx]
            
            for i, pt_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    ct_byte = ciphertext[pos]
                    ks_byte = pt_byte ^ ct_byte
                    keystream[pos] = ks_byte
    
    # Decrypt the target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ciphertext_map:
        result = {'plaintext': '00' * target_length}
    else:
        target_ciphertext = ciphertext_map[target_msg_idx]
        plaintext_bytes = []
        
        for i in range(target_length):
            pos = target_offset + i
            if pos in keystream and pos < len(target_ciphertext):
                ct_byte = target_ciphertext[pos]
                pt_byte = ct_byte ^ keystream[pos]
                plaintext_bytes.append(pt_byte)
            else:
                # Unknown keystream position - shouldn't happen with proper input
                plaintext_bytes.append(0)
        
        plaintext_hex = bytes(plaintext_bytes).hex()
        result = {'plaintext': plaintext_hex}
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
