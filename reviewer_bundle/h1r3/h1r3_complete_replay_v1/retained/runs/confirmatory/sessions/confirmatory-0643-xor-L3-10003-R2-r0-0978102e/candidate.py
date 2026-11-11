import json
import sys
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    # Find maximum length to create keystream array
    max_len = max(len(ct['data']) for ct in ciphertexts)
    
    # Initialize keystream as None (unknown)
    keystream = [None] * max_len
    
    # Process known plaintexts to recover keystream
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
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext_data):
                c_byte = ciphertext_data[pos]
                k_byte = p_byte ^ c_byte
                keystream[pos] = k_byte
    
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
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have the keystream, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    # Convert to hex string
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
