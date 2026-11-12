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
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Find the maximum length we need to consider
    max_len = max(len(ct) for ct in ciphertexts)
    
    # Recover keystream from known plaintexts
    keystream = [None] * max_len
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        ciphertext = ciphertexts[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                # keystream[pos] = plaintext XOR ciphertext
                ks_byte = pt_byte ^ ciphertext[pos]
                keystream[pos] = ks_byte
    
    # Extract target plaintext
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            # plaintext = ciphertext XOR keystream
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    
    # Output
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()