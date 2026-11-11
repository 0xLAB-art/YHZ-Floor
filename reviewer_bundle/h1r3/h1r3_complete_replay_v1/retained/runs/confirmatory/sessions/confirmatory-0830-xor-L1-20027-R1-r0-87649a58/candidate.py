import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the data
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find the ciphertext for target message
    target_ciphertext = None
    for ct in instance['ciphertexts']:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = bytes.fromhex(ct['data'])
            break
    
    # Find known plaintext and corresponding ciphertext
    known_pt = None
    known_ct = None
    for kp in instance['known_plaintexts']:
        kp_msg_idx = kp['message_index']
        kp_offset = kp['offset']
        kp_data = bytes.fromhex(kp['data'])
        
        # Find corresponding ciphertext
        for ct in instance['ciphertexts']:
            if ct['message_index'] == kp_msg_idx:
                known_ct = bytes.fromhex(ct['data'])
                known_pt = kp_data
                break
        
        if known_pt and known_ct:
            break
    
    # Recover keystream from known plaintext: K = C0 XOR P0
    keystream = bytes(c ^ p for c, p in zip(known_ct, known_pt))
    
    # Recover target plaintext: P1 = C1 XOR K
    plaintext = bytes(c ^ k for c, k in zip(target_ciphertext[target_offset:target_offset + target_length], 
                                             keystream[target_offset:target_offset + target_length]))
    
    # Output result
    result = {
        "plaintext": plaintext.hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
