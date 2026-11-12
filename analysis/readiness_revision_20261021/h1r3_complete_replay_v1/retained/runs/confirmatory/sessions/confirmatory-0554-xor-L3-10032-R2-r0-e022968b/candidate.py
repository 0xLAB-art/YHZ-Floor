import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    # Build keystream from known plaintexts
    keystream = {}
    for kp in instance['known_plaintexts']:
        plaintext_data = base64.b64decode(kp['data'])
        message_index = kp['message_index']
        offset = kp['offset']
        
        # Find the corresponding ciphertext
        ciphertext_data = None
        for ct in ciphertexts:
            if ct['message_index'] == message_index:
                ciphertext_data = ct['data']
                break
        
        if ciphertext_data is None:
            continue
        
        # Recover keystream: key = plaintext XOR ciphertext
        for i, plaintext_byte in enumerate(plaintext_data):
            pos = offset + i
            if pos < len(ciphertext_data):
                key_byte = plaintext_byte ^ ciphertext_data[pos]
                keystream[pos] = key_byte
    
    # Decrypt target
    target = instance['target']
    target_message_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_message_index:
            target_ciphertext = ct['data']
            break
    
    # Decrypt using recovered keystream
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            plaintext_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext.append(plaintext_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext.append(0)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext)
    
    # Output result
    result = {'plaintext': plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
