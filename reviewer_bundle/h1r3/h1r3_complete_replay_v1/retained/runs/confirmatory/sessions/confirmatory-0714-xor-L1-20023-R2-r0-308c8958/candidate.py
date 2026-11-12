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
    
    # Build a mapping of message_index to ciphertext
    ct_map = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_data = base64.b64decode(ct['data'])
        ct_map[msg_idx] = ct_data
    
    # Build a mapping of (message_index, offset) to known plaintext
    pt_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = base64.b64decode(kp['data'])
        pt_map[(msg_idx, offset)] = pt_data
    
    # Extract target parameters
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find a known plaintext that can help us
    # In a stream cipher reuse attack, if two messages use the same keystream:
    # C1 = P1 XOR K
    # C2 = P2 XOR K
    # Therefore: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can find P2: P2 = P1 XOR C1 XOR C2
    
    # Look for a known plaintext we can use
    for (kp_msg_idx, kp_offset), kp_data in pt_map.items():
        # Check if this known plaintext overlaps with what we need
        if kp_msg_idx == target_msg_idx:
            # Same message, just extract
            start = target_offset - kp_offset
            end = start + target_length
            if start >= 0 and end <= len(kp_data):
                result = kp_data[start:end]
                print(json.dumps({"plaintext": result.hex()}))
                return
        else:
            # Different messages - use XOR attack
            # We need the ciphertexts to overlap in the keystream
            # Assuming same keystream is used starting from offset 0 in both messages
            
            # Get ciphertexts
            ct_known = ct_map.get(kp_msg_idx)
            ct_target = ct_map.get(target_msg_idx)
            
            if ct_known and ct_target:
                # Extract the relevant portions
                # Known plaintext at kp_offset in message kp_msg_idx
                # We want to recover plaintext at target_offset in message target_msg_idx
                
                # Compute keystream from known message
                keystream_start = kp_offset
                keystream_end = kp_offset + len(kp_data)
                
                # Check if target region overlaps with our known keystream
                if target_offset >= keystream_start and target_offset + target_length <= keystream_end:
                    # Extract keystream: K = P1 XOR C1
                    ct_segment = ct_known[kp_offset:kp_offset + len(kp_data)]
                    keystream = bytes(a ^ b for a, b in zip(kp_data, ct_segment))
                    
                    # Use keystream to decrypt target: P2 = C2 XOR K
                    ks_offset = target_offset - keystream_start
                    target_keystream = keystream[ks_offset:ks_offset + target_length]
                    ct_target_segment = ct_target[target_offset:target_offset + target_length]
                    
                    result = bytes(a ^ b for a, b in zip(ct_target_segment, target_keystream))
                    print(json.dumps({"plaintext": result.hex()}))
                    return
    
    # Fallback: empty result
    print(json.dumps({"plaintext": "00" * target_length}))

if __name__ == "__main__":
    main()
