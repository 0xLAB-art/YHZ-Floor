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
    
    # Extract target information
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # We have a known plaintext for message 0
    # We can use this to recover the keystream
    known_msg_idx = 0
    known_plaintext = kp_map[known_msg_idx]['data']
    known_offset = kp_map[known_msg_idx]['offset']
    ciphertext_0 = ct_map[known_msg_idx]
    
    # For a stream cipher (like XOR with keystream):
    # C = P XOR K, so K = P XOR C
    keystream = bytes(p ^ c for p, c in zip(known_plaintext, ciphertext_0[known_offset:known_offset + len(known_plaintext)]))
    
    # Now decrypt the target message using the recovered keystream
    ciphertext_target = ct_map[target_msg_idx]
    
    # Extract the target portion
    target_ciphertext = ciphertext_target[target_offset:target_offset + target_length]
    
    # Decrypt: P = C XOR K
    plaintext = bytes(c ^ k for c, k in zip(target_ciphertext, keystream[target_offset:target_offset + target_length]))
    
    # Convert to hex
    plaintext_hex = plaintext.hex()
    
    # Output
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
