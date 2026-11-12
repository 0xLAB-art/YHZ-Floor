import sys
import json
import base64
from collections import defaultdict

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
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        plaintext = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': plaintext,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Build keystream recovery map
    keystream = {}
    
    # Recover keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['data']
        ciphertext = ciphertexts[msg_idx]['data']
        
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = c_byte ^ p_byte
                keystream[pos] = k_byte
    
    # Decrypt target using recovered keystream
    target_ciphertext = ciphertexts[target_msg_idx]['data']
    plaintext_bytes = bytearray()
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If keystream not recovered, try zero (shouldn't happen with good data)
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = plaintext_bytes.hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
