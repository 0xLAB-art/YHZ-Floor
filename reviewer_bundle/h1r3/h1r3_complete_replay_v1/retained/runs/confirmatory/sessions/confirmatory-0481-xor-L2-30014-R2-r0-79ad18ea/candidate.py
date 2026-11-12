import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Decode known plaintexts
    known = []
    for kp in instance['known_plaintexts']:
        plaintext = base64.b64decode(kp['data'])
        known.append({
            'plaintext': plaintext,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target_msg = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    for kp in known:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['plaintext']
        ciphertext = ciphertexts[msg_idx]
        
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = c_byte ^ p_byte
                keystream[pos] = k_byte
    
    # Decrypt target using recovered keystream
    target_ciphertext = ciphertexts[target_msg]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            c_byte = target_ciphertext[pos]
            k_byte = keystream[pos]
            p_byte = c_byte ^ k_byte
            plaintext_bytes.append(p_byte)
        else:
            # Shouldn't happen if we have enough known plaintext
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
