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
    
    # Find a known plaintext to use for key recovery
    # We have plaintext for message 0 at offset 0
    known_msg_idx = 0
    known_pt = kp_map[known_msg_idx]['data']
    known_offset = kp_map[known_msg_idx]['offset']
    known_ct = ct_map[known_msg_idx]
    
    # Recover the keystream for message 0
    # keystream = plaintext XOR ciphertext
    keystream = bytes(p ^ c for p, c in zip(known_pt, known_ct[known_offset:known_offset+len(known_pt)]))
    
    # Get target ciphertext
    target_ct = ct_map[target_msg_idx]
    
    # Decrypt target using the recovered keystream
    # This works if the same keystream is reused (stream cipher nonce reuse)
    plaintext_bytes = bytes(c ^ k for c, k in zip(target_ct[target_offset:target_offset+target_length], keystream[:target_length]))
    
    # Convert to hex
    plaintext_hex = plaintext_bytes.hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()