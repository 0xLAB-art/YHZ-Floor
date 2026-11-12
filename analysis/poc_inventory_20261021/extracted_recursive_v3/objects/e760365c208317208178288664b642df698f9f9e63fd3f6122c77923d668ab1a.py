import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Decode ciphertexts
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = base64.b64decode(ct['data'])
    
    # Decode known plaintexts
    kp_map = {}
    for kp in known_plaintexts:
        kp_map[kp['message_index']] = {
            'data': base64.b64decode(kp['data']),
            'offset': kp['offset']
        }
    
    # Extract target info
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get the known plaintext for message 0
    known_pt_info = kp_map[0]
    known_pt = known_pt_info['data']
    known_offset = known_pt_info['offset']
    
    # Get ciphertext for message 0
    ct0 = ct_map[0]
    
    # Recover the keystream for message 0
    # keystream = plaintext XOR ciphertext
    keystream = bytes(p ^ c for p, c in zip(known_pt, ct0[known_offset:known_offset + len(known_pt)]))
    
    # Get ciphertext for target message
    ct_target = ct_map[target_msg_idx]
    
    # Decrypt the target using the recovered keystream
    # plaintext = ciphertext XOR keystream
    plaintext = bytes(ct_target[target_offset + i] ^ keystream[i] 
                     for i in range(target_length))
    
    # Output as lowercase hex
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()