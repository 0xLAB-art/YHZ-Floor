import json
import sys
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
    
    # Find a known plaintext for the target message or use XOR properties
    # If we have known plaintext for message 0 and ciphertext for messages 0 and 1,
    # we can recover the keystream from message 0 and apply it to message 1
    
    # Get known plaintext from message 0
    kp_msg_idx = 0
    kp_data = kp_map[kp_msg_idx]['data']
    kp_offset = kp_map[kp_msg_idx]['offset']
    
    # Get ciphertext for message with known plaintext
    ct_known = ct_map[kp_msg_idx]
    
    # Recover keystream: keystream = plaintext XOR ciphertext
    keystream = bytes(p ^ c for p, c in zip(kp_data, ct_known[kp_offset:kp_offset + len(kp_data)]))
    
    # Get target ciphertext
    ct_target = ct_map[target_msg_idx]
    
    # Decrypt target: plaintext = ciphertext XOR keystream
    plaintext_bytes = bytes(c ^ k for c, k in zip(
        ct_target[target_offset:target_offset + target_length],
        keystream[:target_length]
    ))
    
    # Convert to lowercase hex
    plaintext_hex = plaintext_bytes.hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
