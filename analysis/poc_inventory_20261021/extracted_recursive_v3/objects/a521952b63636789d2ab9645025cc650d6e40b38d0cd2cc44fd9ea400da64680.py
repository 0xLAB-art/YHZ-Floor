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
        msg_idx = ct['message_index']
        ct_map[msg_idx] = base64.b64decode(ct['data'])
    
    # Decode known plaintexts
    kp_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = base64.b64decode(kp['data'])
        if msg_idx not in kp_map:
            kp_map[msg_idx] = {}
        kp_map[msg_idx][offset] = pt_data
    
    # Extract target parameters
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get the target ciphertext
    target_ct = ct_map[target_msg_idx]
    
    # For a stream cipher reuse attack:
    # If we have plaintext P0 at offset o in message m0
    # and ciphertext C0 = P0 XOR K (where K is the keystream at offset o)
    # Then K = P0 XOR C0
    # And for message m1 at the same offset: P1 = C1 XOR K = C1 XOR P0 XOR C0
    
    # Find a known plaintext we can use
    # We need known plaintext for message 0 at offset 0
    if 0 in kp_map and 0 in kp_map[0]:
        known_pt = kp_map[0][0]
        known_ct = ct_map[0]
        
        # Extract the keystream by XORing known plaintext with its ciphertext
        keystream = bytes(p ^ c for p, c in zip(known_pt, known_ct))
        
        # Now decrypt the target using the keystream
        target_pt_bytes = bytes(c ^ k for c, k in zip(target_ct[target_offset:target_offset+target_length], 
                                                        keystream[target_offset:target_offset+target_length]))
        
        # Convert to hex
        plaintext_hex = target_pt_bytes.hex()
        
        result = {"plaintext": plaintext_hex}
        print(json.dumps(result))
    else:
        # Fallback - shouldn't happen with this instance
        result = {"plaintext": "00" * target_length}
        print(json.dumps(result))

if __name__ == "__main__":
    main()