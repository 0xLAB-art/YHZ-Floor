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
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Build keystream from known plaintexts
    keystream = {}
    for kp in instance['known_plaintexts']:
        plaintext_bytes = base64.b64decode(kp['data'])
        msg_idx = kp['message_index']
        offset = kp['offset']
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertexts[msg_idx][pos]
            key_byte = ct_byte ^ pt_byte
            keystream[pos] = key_byte
    
    # Decrypt target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = ciphertexts[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Should not happen if keystream is complete
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()