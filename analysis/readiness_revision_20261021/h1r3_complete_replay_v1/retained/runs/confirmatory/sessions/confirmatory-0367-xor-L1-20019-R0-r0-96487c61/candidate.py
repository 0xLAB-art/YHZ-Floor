import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex strings to bytes
    ciphertext_map = {}
    for ct in ciphertexts:
        ciphertext_map[ct['message_index']] = bytes.fromhex(ct['data'])
    
    known_pt_map = {}
    for kpt in known_plaintexts:
        known_pt_map[kpt['message_index']] = {
            'data': bytes.fromhex(kpt['data']),
            'offset': kpt['offset']
        }
    
    # Extract target information
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get the known plaintext and its corresponding ciphertext
    # Known plaintext is for message_index 0
    known_msg_idx = 0
    known_pt = known_pt_map[known_msg_idx]['data']
    known_pt_offset = known_pt_map[known_msg_idx]['offset']
    known_ct = ciphertext_map[known_msg_idx]
    
    # Extract the portion of ciphertext corresponding to known plaintext
    known_ct_portion = known_ct[known_pt_offset:known_pt_offset + len(known_pt)]
    
    # Derive the keystream by XORing known plaintext with its ciphertext
    keystream = bytes(p ^ c for p, c in zip(known_pt, known_ct_portion))
    
    # Get target ciphertext
    target_ct = ciphertext_map[target_msg_idx]
    target_ct_portion = target_ct[target_offset:target_offset + target_length]
    
    # Decrypt target by XORing with keystream
    # Assuming the same keystream is reused at the same positions
    plaintext = bytes(c ^ k for c, k in zip(target_ct_portion, keystream[:len(target_ct_portion)]))
    
    # Output result
    result = {
        "plaintext": plaintext.hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
