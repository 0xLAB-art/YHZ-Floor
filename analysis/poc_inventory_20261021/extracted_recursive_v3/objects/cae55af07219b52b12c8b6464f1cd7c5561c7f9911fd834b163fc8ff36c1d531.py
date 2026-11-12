import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ciphertext_bytes = []
    for ct in ciphertexts:
        ciphertext_bytes.append(bytes.fromhex(ct['data']))
    
    # Recover keystream
    # keystream[position] = plaintext[position] XOR ciphertext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_data = bytes.fromhex(kp['data'])
        
        ciphertext = ciphertext_bytes[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_data):
            position = offset + i
            ct_byte = ciphertext[position]
            keystream[position] = pt_byte ^ ct_byte
    
    # Decrypt target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_bytes[target_msg_idx]
    
    plaintext = []
    for i in range(target_length):
        position = target_offset + i
        if position in keystream:
            # Decrypt using recovered keystream
            ct_byte = target_ciphertext[position]
            pt_byte = ct_byte ^ keystream[position]
            plaintext.append(pt_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            # But handle it gracefully
            plaintext.append(0)
    
    plaintext_hex = bytes(plaintext).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()