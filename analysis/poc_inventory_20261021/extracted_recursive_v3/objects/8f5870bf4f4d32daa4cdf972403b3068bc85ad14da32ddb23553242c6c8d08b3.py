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
    
    # Get the known plaintext for message 0
    known_pt_msg0 = kp_map[0][0]
    ct_msg0 = ct_map[0]
    
    # Recover the keystream for message 0
    # C0 = P0 XOR K
    # K = C0 XOR P0
    keystream = bytes(c ^ p for c, p in zip(ct_msg0, known_pt_msg0))
    
    # Now recover plaintext for target message using the same keystream
    # P1 = C1 XOR K
    ct_target = ct_map[target_msg_idx]
    
    # Extract the target portion
    end_offset = target_offset + target_length
    plaintext_bytes = bytes(c ^ k for c, k in zip(
        ct_target[target_offset:end_offset],
        keystream[target_offset:end_offset]
    ))
    
    # Convert to hex
    plaintext_hex = plaintext_bytes.hex()
    
    # Output
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()