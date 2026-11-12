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
    target_length = instance['target']['length']
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    
    # Find target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = ct['data']
            break
    
    # Recover keystream bytes
    # keystream[position] = plaintext[i] XOR ciphertext[position]
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
        
        if ciphertext_data is None:
            continue
        
        # Recover keystream bytes at this position
        for i, pt_byte in enumerate(plaintext_data):
            pos = offset + i
            if pos < len(ciphertext_data):
                ct_byte = ciphertext_data[pos]
                ks_byte = pt_byte ^ ct_byte
                keystream[pos] = ks_byte
    
    # Decrypt target using recovered keystream
    plaintext_bytes = bytearray()
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream at this position, we can't decrypt
            # This shouldn't happen if the challenge is solvable
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = plaintext_bytes.hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
