import sys
import json
import base64
from typing import Dict, List, Tuple

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
    target_length = target['length']
    target_message_index = target['message_index']
    target_offset = target['offset']
    
    # Find the ciphertext for the target message
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_message_index:
            target_ciphertext = ct['data']
            break
    
    # Build a keystream recovery map
    # For stream cipher reuse attacks: C = P XOR K
    # If we know P and C at position i, we can recover K[i] = P[i] XOR C[i]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['data']
        
        # Find corresponding ciphertext
        ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext:
            # Recover keystream bytes
            for i, p_byte in enumerate(plaintext):
                pos = offset + i
                if pos < len(ciphertext):
                    c_byte = ciphertext[pos]
                    k_byte = p_byte ^ c_byte
                    keystream[pos] = k_byte
    
    # Now decrypt the target using recovered keystream
    result = []
    for i in range(target_offset, target_offset + target_length):
        if i in keystream and i < len(target_ciphertext):
            k_byte = keystream[i]
            c_byte = target_ciphertext[i]
            p_byte = c_byte ^ k_byte
            result.append(p_byte)
        else:
            # If we don't have keystream for this position, we need to infer it
            # This is a many-time pad attack - try XORing with other messages
            # and look for patterns
            result.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(result).hex()
    
    output = {
        "plaintext": plaintext_hex
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()