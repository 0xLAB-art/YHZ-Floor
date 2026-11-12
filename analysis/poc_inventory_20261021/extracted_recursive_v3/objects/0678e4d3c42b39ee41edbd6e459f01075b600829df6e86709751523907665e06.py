import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    # Parse known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': data,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    # Target
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Recover keystream
    # We assume all messages use the same keystream (stream cipher key reuse)
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        # Get corresponding ciphertext
        ciphertext_data = ciphertexts[msg_idx]['data']
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertext_data[pos]
            ks_byte = pt_byte ^ ct_byte
            keystream[pos] = ks_byte
    
    # Decrypt target using recovered keystream
    target_ciphertext = ciphertexts[target_msg_idx]['data']
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt
            # This shouldn't happen if the instance is solvable
            plaintext.append(0)
    
    # Convert to hex string
    plaintext_hex = bytes(plaintext).hex()
    
    # Output result
    result = {
        "plaintext": plaintext_hex
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()
