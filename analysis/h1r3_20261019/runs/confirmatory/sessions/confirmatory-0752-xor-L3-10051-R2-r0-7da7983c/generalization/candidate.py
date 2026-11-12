import sys
import json
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
    
    # Find maximum length needed
    max_len = instance['target']['offset'] + instance['target']['length']
    
    # Initialize keystream recovery (None means unknown)
    keystream = [None] * max_len
    
    # Process each known plaintext
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        
        # Find the corresponding ciphertext
        ciphertext_data = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext_data = ct['data']
                break
        
        if ciphertext_data is None:
            continue
        
        # XOR plaintext with ciphertext to recover keystream
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext_data):
                c_byte = ciphertext_data[pos]
                k_byte = p_byte ^ c_byte
                
                # Store recovered keystream byte
                if keystream[pos] is None:
                    keystream[pos] = k_byte
                elif keystream[pos] != k_byte:
                    # Consistency check - if we get different values, something is wrong
                    # but we'll use the first value we found
                    pass
    
    # Now decrypt the target using recovered keystream
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Find target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = ct['data']
            break
    
    # Decrypt target
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have keystream, we can't decrypt
            # This shouldn't happen if the challenge is solvable
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
