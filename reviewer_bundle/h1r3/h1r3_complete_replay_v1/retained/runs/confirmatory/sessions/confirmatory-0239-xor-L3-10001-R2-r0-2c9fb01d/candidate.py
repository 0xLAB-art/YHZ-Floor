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
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': data,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    # Get target info
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find the target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = ct['data']
            break
    
    # Recover keystream from known plaintexts
    # keystream[position] = ciphertext[position] XOR plaintext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_data = kp['data']
        
        # Find corresponding ciphertext
        ciphertext_data = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext_data = ct['data']
                break
        
        if ciphertext_data:
            # Recover keystream at these positions
            for i, pt_byte in enumerate(plaintext_data):
                pos = offset + i
                if pos < len(ciphertext_data):
                    ct_byte = ciphertext_data[pos]
                    ks_byte = ct_byte ^ pt_byte
                    keystream[pos] = ks_byte
    
    # Decrypt target using recovered keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Should not happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
