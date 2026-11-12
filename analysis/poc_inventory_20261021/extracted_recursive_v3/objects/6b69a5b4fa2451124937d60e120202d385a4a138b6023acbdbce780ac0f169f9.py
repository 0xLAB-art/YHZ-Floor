import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Decode ciphertexts
    ct_dict = {}
    for ct in ciphertexts:
        ct_dict[ct['message_index']] = base64.b64decode(ct['data'])
    
    # Decode known plaintexts
    kp_dict = {}
    for kp in known_plaintexts:
        kp_dict[kp['message_index']] = {
            'data': base64.b64decode(kp['data']),
            'offset': kp['offset']
        }
    
    # Extract keystream from known plaintext
    # For stream cipher: ciphertext = plaintext XOR keystream
    # So: keystream = plaintext XOR ciphertext
    
    known_msg_idx = list(kp_dict.keys())[0]
    known_pt = kp_dict[known_msg_idx]['data']
    known_offset = kp_dict[known_msg_idx]['offset']
    known_ct = ct_dict[known_msg_idx]
    
    # Extract keystream at the known offset
    keystream = bytes(p ^ c for p, c in zip(known_pt, known_ct[known_offset:known_offset+len(known_pt)]))
    
    # Now decrypt the target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_dict[target_msg_idx]
    
    # Decrypt using the recovered keystream
    plaintext = bytes(c ^ k for c, k in zip(
        target_ct[target_offset:target_offset+target_length],
        keystream[:target_length]
    ))
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()