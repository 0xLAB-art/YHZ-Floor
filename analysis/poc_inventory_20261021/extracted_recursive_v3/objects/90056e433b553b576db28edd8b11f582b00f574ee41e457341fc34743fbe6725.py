import json
import sys

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    # Get known plaintext
    known_pt = instance['known_plaintexts'][0]
    known_plaintext = bytes.fromhex(known_pt['data'])
    known_msg_idx = known_pt['message_index']
    known_offset = known_pt['offset']
    
    # Get target information
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Recover keystream from known plaintext
    known_ciphertext = ciphertexts[known_msg_idx]
    keystream_segment = bytes(p ^ c for p, c in zip(known_plaintext, 
                              known_ciphertext[known_offset:known_offset + len(known_plaintext)]))
    
    # Decrypt target using the keystream
    target_ciphertext = ciphertexts[target_msg_idx]
    target_ct_portion = target_ciphertext[target_offset:target_offset + target_length]
    keystream_for_target = keystream_segment[target_offset - known_offset:
                                             target_offset - known_offset + target_length]
    
    plaintext = bytes(c ^ k for c, k in zip(target_ct_portion, keystream_for_target))
    
    # Output result
    print(json.dumps({"plaintext": plaintext.hex()}))

if __name__ == "__main__":
    main()