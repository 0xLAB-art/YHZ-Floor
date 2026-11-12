import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        data = base64.b64decode(ct['data'])
        ciphertexts[idx] = data
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        idx = kp['message_index']
        offset = kp['offset']
        data = base64.b64decode(kp['data'])
        if idx not in known_plaintexts:
            known_plaintexts[idx] = {}
        known_plaintexts[idx][offset] = data
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    known_msg_idx = 0
    known_offset = 0
    known_plaintext = known_plaintexts[known_msg_idx][known_offset]
    
    ciphertext_known = ciphertexts[known_msg_idx]
    ciphertext_target = ciphertexts[target_msg_idx]
    
    keystream_len = len(known_plaintext)
    keystream = bytes(known_plaintext[i] ^ ciphertext_known[known_offset + i] 
                     for i in range(keystream_len))
    
    plaintext_bytes = bytes(ciphertext_target[target_offset + i] ^ keystream[i] 
                           for i in range(target_length))
    
    plaintext_hex = plaintext_bytes.hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()