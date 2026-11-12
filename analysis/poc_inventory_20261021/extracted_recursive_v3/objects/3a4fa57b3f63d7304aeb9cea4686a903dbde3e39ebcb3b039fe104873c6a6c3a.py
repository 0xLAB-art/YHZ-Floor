import sys
import json
import base64

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts from base64
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Recover keystream from known plaintexts
    # For a stream cipher: ciphertext = plaintext XOR keystream
    # Therefore: keystream = plaintext XOR ciphertext
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        # Recover keystream bytes at these positions
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertexts[msg_idx][pos]
            ks_byte = pt_byte ^ ct_byte
            keystream[pos] = ks_byte
    
    # Decrypt the target message
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        ct_byte = ciphertexts[target_msg_idx][pos]
        ks_byte = keystream[pos]
        pt_byte = ct_byte ^ ks_byte
        plaintext.append(pt_byte)
    
    # Convert to lowercase hex string
    plaintext_hex = bytes(plaintext).hex()
    
    # Output exactly one JSON object
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == '__main__':
    main()