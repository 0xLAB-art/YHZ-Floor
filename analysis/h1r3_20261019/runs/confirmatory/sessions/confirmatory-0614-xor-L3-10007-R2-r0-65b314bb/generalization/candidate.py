import json
import sys
import base64

def main():
    # Read instance from command line argument
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
    
    # Extract target information
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Find target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = ct['data']
            break
    
    # Recover keystream bytes
    # keystream[position] = plaintext XOR ciphertext
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        # Find corresponding ciphertext
        ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext is None:
            continue
        
        # Recover keystream at this position
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                ct_byte = ciphertext[pos]
                ks_byte = pt_byte ^ ct_byte
                keystream[pos] = ks_byte
    
    # Decrypt target using recovered keystream
    plaintext = bytearray(target_length)
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            plaintext[i] = target_ciphertext[pos] ^ keystream[pos]
        else:
            # If we don't have keystream at this position, we have a problem
            # This shouldn't happen with a properly constructed instance
            plaintext[i] = 0
    
    # Convert to hex
    plaintext_hex = plaintext.hex()
    
    # Output result
    result = {
        "plaintext": plaintext_hex
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
