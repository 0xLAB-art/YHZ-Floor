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
    
    # Decode known plaintext
    kp = known_plaintexts[0]
    known_pt = base64.b64decode(kp['data'])
    known_msg_idx = kp['message_index']
    known_offset = kp['offset']
    
    # Get target info
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get the ciphertexts
    ct_known = ct_map[known_msg_idx]
    ct_target = ct_map[target_msg_idx]
    
    # Extract the keystream from known plaintext
    # For stream cipher: C = P XOR K, so K = C XOR P
    keystream_segment = bytes(c ^ p for c, p in zip(
        ct_known[known_offset:known_offset + len(known_pt)],
        known_pt
    ))
    
    # Use the keystream to decrypt the target
    # P = C XOR K
    plaintext = bytes(c ^ k for c, k in zip(
        ct_target[target_offset:target_offset + target_length],
        keystream_segment[:target_length]
    ))
    
    # Convert to hex
    plaintext_hex = plaintext.hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()