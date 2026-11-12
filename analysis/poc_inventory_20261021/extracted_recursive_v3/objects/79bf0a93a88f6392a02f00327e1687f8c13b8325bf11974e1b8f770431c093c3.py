import base64
import json
import sys

def main():
    # Read instance from command line argument
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
    
    # Find the maximum position we need to recover
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    target_msg_idx = instance['target']['message_index']
    max_pos = target_offset + target_length
    
    # Initialize keystream recovery (None means unknown)
    keystream = [None] * max_pos
    
    # Process all known plaintexts to recover keystream
    for kp in instance['known_plaintexts']:
        plaintext_data = base64.b64decode(kp['data'])
        msg_idx = kp['message_index']
        offset = kp['offset']
        
        # Find the corresponding ciphertext
        ciphertext_data = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext_data = ct['data']
                break
        
        # Recover keystream bytes by XORing known plaintext with ciphertext
        for i, pt_byte in enumerate(plaintext_data):
            pos = offset + i
            if pos < max_pos:
                ct_byte = ciphertext_data[pos]
                keystream[pos] = pt_byte ^ ct_byte
    
    # Get target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = ct['data']
            break
    
    # Decrypt target using recovered keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if keystream[pos] is not None:
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If keystream byte is unknown, we have a problem
            # But the problem should be solvable with given knowns
            plaintext_bytes.append(0)  # fallback
    
    # Convert to hex string
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    
    # Output result
    result = {'plaintext': plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()