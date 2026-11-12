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
        ciphertexts.append(data)
    
    # Recover keystream from known plaintexts
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_data = base64.b64decode(kp['data'])
        
        # Extract corresponding ciphertext bytes
        ciphertext = ciphertexts[msg_idx]
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(plaintext_data):
            pos = offset + i
            if pos < len(ciphertext):
                ct_byte = ciphertext[pos]
                ks_byte = pt_byte ^ ct_byte
                keystream[pos] = ks_byte
    
    # Now decrypt the target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    target_ciphertext = ciphertexts[target_msg_idx]
    
    # Decrypt using recovered keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream for this position, we have a problem
            # Try to see if we can infer it from other messages
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
