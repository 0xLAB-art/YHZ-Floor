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
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        if msg_idx not in kp_map:
            kp_map[msg_idx] = {}
        kp_map[msg_idx][offset] = plaintext
    
    # Extract target information
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get the known plaintext for message 0 at offset 0
    known_pt_0 = kp_map[0][0]
    ct_0 = ct_map[0]
    
    # Recover the keystream for message 0
    # In a stream cipher: ciphertext = plaintext XOR keystream
    # So: keystream = plaintext XOR ciphertext
    keystream = bytes(p ^ c for p, c in zip(known_pt_0, ct_0))
    
    # For stream ciphers with nonce reuse, the same keystream is used
    # Recover the plaintext for the target message
    ct_target = ct_map[target_msg_idx]
    
    # Extract the portion we need
    target_ct = ct_target[target_offset:target_offset + target_length]
    target_keystream = keystream[target_offset:target_offset + target_length]
    
    # Decrypt: plaintext = ciphertext XOR keystream
    plaintext = bytes(c ^ k for c, k in zip(target_ct, target_keystream))
    
    # Convert to hex
    plaintext_hex = plaintext.hex()
    
    # Output
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()