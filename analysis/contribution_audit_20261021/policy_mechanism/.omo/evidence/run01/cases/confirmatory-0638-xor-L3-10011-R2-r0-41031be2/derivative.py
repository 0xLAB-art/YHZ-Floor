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
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        plaintext_bytes = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': plaintext_bytes,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Create cipher array indexed by message_index
    cipher_by_idx = {}
    for ct in ciphertexts:
        cipher_by_idx[ct['message_index']] = ct['data']
    
    # Recover keystream bytes using known plaintexts
    # keystream[position] = ciphertext[position] XOR plaintext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['data']
        ciphertext = cipher_by_idx[msg_idx]
        
        for i, pt_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                ct_byte = ciphertext[pos]
                ks_byte = ct_byte ^ pt_byte
                keystream[pos] = ks_byte
    
    # Decrypt target using recovered keystream
    target_ciphertext = cipher_by_idx[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If keystream not known at this position, we have a problem
            # Try crib-dragging or statistical analysis
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
