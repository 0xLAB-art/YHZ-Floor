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
        plaintext_bytes = base64.b64decode(kp['data'])
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
        
        # Recover keystream bytes: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext_data):
                ct_byte = ciphertext_data[pos]
                ks_byte = pt_byte ^ ct_byte
                
                # Store keystream with (message_index, position) as key
                key = (message_index, pos)
                if key not in keystream:
                    keystream[key] = ks_byte
    
    # Extract target info
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
    
    # Decrypt target using recovered keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        key = (target_message_index, pos)
        
        if key in keystream and pos < len(target_ciphertext):
            ct_byte = target_ciphertext[pos]
            ks_byte = keystream[key]
            pt_byte = ct_byte ^ ks_byte
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt it
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
