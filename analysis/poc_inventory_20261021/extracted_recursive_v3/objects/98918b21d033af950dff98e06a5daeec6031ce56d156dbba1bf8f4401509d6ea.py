import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        data = base64.b64decode(ct['data'])
        ciphertexts[idx] = data
    
    # Recover keystream from known plaintexts
    keystream = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        ciphertext = ciphertexts[msg_idx]
        
        # XOR plaintext with ciphertext to get keystream
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            c_byte = ciphertext[pos]
            k_byte = p_byte ^ c_byte
            keystream[pos] = k_byte
    
    # Decrypt target
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertexts[target_msg_idx]
    target_plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            target_plaintext.append(p_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            target_plaintext.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(target_plaintext).hex()
    
    # Output
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
