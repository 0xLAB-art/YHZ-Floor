import sys
import json
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
    
    target = instance['target']
    target_length = target['length']
    target_msg_index = target['message_index']
    target_offset = target['offset']
    
    # Find the target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_index:
            target_ciphertext = ct['data']
            break
    
    # Recover keystream bytes using known plaintexts
    # keystream[offset] = ciphertext[offset] XOR plaintext[offset]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        # Find the corresponding ciphertext
        ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext:
            # Recover keystream bytes at these offsets
            for i, pt_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    ks_byte = ciphertext[pos] ^ pt_byte
                    keystream[pos] = ks_byte
    
    # Now decrypt the target using the recovered keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have the keystream byte, we have a problem
            # For now, use 0 as fallback (shouldn't happen with valid input)
            plaintext_bytes.append(0)
    
    # Convert to hex string
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output exactly one JSON object
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()