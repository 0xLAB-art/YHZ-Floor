import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        msg_idx = ct['message_index']
        ciphertexts[msg_idx] = data
    
    # Build keystream from known plaintexts
    keystream = {}
    for kp in instance['known_plaintexts']:
        plaintext_data = base64.b64decode(kp['data'])
        msg_idx = kp['message_index']
        offset = kp['offset']
        
        ciphertext = ciphertexts[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_data):
            pos = offset + i
            ct_byte = ciphertext[pos]
            keystream[pos] = ct_byte ^ pt_byte
    
    # Decrypt target
    target = instance['target']
    target_ciphertext = ciphertexts[target['message_index']]
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            plaintext_bytes.append(0)
    
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == '__main__':
    main()