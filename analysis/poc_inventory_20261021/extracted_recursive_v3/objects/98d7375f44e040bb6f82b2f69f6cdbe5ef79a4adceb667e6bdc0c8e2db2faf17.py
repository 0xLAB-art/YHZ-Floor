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
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_data = base64.b64decode(kp['data'])
        if msg_idx not in kp_map:
            kp_map[msg_idx] = {}
        kp_map[msg_idx][offset] = plaintext_data
    
    # Extract target information
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # This appears to be a stream cipher reuse attack
    # If the same keystream is used for multiple messages:
    # C1 = P1 XOR K
    # C2 = P2 XOR K
    # Therefore: C1 XOR P1 = K
    # And: P2 = C2 XOR K = C2 XOR C1 XOR P1
    
    # Find a known plaintext we can use to recover keystream
    keystream = None
    keystream_msg_idx = None
    
    for msg_idx, offsets in kp_map.items():
        for offset, plaintext in offsets.items():
            if msg_idx in ct_map:
                # Recover keystream: K = C XOR P
                ciphertext = ct_map[msg_idx]
                # Extract the portion corresponding to this known plaintext
                ct_segment = ciphertext[offset:offset+len(plaintext)]
                
                # XOR to get keystream
                ks = bytes([c ^ p for c, p in zip(ct_segment, plaintext)])
                keystream = ks
                keystream_msg_idx = msg_idx
                keystream_offset = offset
                break
    
    # Now use the keystream to decrypt the target
    target_ciphertext = ct_map[target_msg_idx]
    target_ct_segment = target_ciphertext[target_offset:target_offset+target_length]
    
    # If we have the keystream from the same offset, we can decrypt directly
    # P_target = C_target XOR K
    plaintext_bytes = bytes([c ^ k for c, k in zip(target_ct_segment, keystream)])
    
    # Convert to hex
    plaintext_hex = plaintext_bytes.hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()