import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Decode all ciphertexts from base64
    decoded_ciphertexts = []
    for ct in ciphertexts:
        decoded_ciphertexts.append(base64.b64decode(ct['data']))
    
    # Build a keystream recovery map
    # For each known plaintext, we can recover keystream bytes
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        ciphertext = decoded_ciphertexts[msg_idx]
        
        # XOR to recover keystream: keystream = plaintext XOR ciphertext
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                k_byte = p_byte ^ ciphertext[pos]
                keystream[pos] = k_byte
    
    # Now recover the target plaintext using the keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = decoded_ciphertexts[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            # Decrypt: plaintext = ciphertext XOR keystream
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If keystream is not available, we cannot decrypt
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
