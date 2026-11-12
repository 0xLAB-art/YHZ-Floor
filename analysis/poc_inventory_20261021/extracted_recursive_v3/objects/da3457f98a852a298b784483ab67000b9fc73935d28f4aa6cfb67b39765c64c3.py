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
        ciphertexts.append({
            'data': base64.b64decode(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Build keystream recovery map
    # keystream[position] = key_byte at that position
    keystream = {}
    
    # Process each known plaintext
    for kp in instance['known_plaintexts']:
        plaintext_bytes = base64.b64decode(kp['data'])
        message_index = kp['message_index']
        offset = kp['offset']
        
        # Find the ciphertext for this message
        ciphertext_data = None
        for ct in ciphertexts:
            if ct['message_index'] == message_index:
                ciphertext_data = ct['data']
                break
        
        if ciphertext_data is None:
            continue
        
        # Recover keystream bytes: key = plaintext XOR ciphertext
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext_data):
                ct_byte = ciphertext_data[pos]
                key_byte = pt_byte ^ ct_byte
                keystream[pos] = key_byte
    
    # Get target ciphertext
    target_message_index = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_message_index:
            target_ciphertext = ct['data']
            break
    
    # Decrypt target using recovered keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            ct_byte = target_ciphertext[pos]
            key_byte = keystream[pos]
            pt_byte = ct_byte ^ key_byte
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {
        'plaintext': plaintext_hex
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()