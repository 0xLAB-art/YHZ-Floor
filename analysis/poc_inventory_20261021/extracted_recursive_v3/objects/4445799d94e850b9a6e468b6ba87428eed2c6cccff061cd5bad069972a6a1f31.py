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
    ct_dict = {}
    for ct in ciphertexts:
        ct_dict[ct['message_index']] = base64.b64decode(ct['data'])
    
    # Decode known plaintexts
    kp_dict = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        if msg_idx not in kp_dict:
            kp_dict[msg_idx] = {}
        kp_dict[msg_idx][offset] = plaintext
    
    # This appears to be a stream cipher reuse attack
    # If the same keystream is used for multiple messages:
    # C1 = P1 XOR K
    # C2 = P2 XOR K
    # Therefore: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can recover P2: P2 = P1 XOR C1 XOR C2
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find a known plaintext we can use
    # We need a known plaintext from a different message at the same offset
    for kp_msg_idx in kp_dict:
        if kp_msg_idx == target_msg_idx:
            continue
        
        for kp_offset, known_pt in kp_dict[kp_msg_idx].items():
            # Check if this known plaintext overlaps with our target
            if kp_offset <= target_offset < kp_offset + len(known_pt):
                # We can use this!
                # Extract the relevant portion of the known plaintext
                start_in_kp = target_offset - kp_offset
                end_in_kp = start_in_kp + target_length
                
                if end_in_kp <= len(known_pt):
                    # The known plaintext fully covers our target
                    relevant_kp = known_pt[start_in_kp:end_in_kp]
                    
                    # Get the corresponding ciphertext bytes
                    kp_ct = ct_dict[kp_msg_idx][target_offset:target_offset + target_length]
                    target_ct = ct_dict[target_msg_idx][target_offset:target_offset + target_length]
                    
                    # Recover the target plaintext
                    # P_target = P_known XOR C_known XOR C_target
                    target_pt = bytes(
                        relevant_kp[i] ^ kp_ct[i] ^ target_ct[i]
                        for i in range(target_length)
                    )
                    
                    # Convert to hex
                    result = target_pt.hex()
                    print(json.dumps({"plaintext": result}))
                    return

if __name__ == "__main__":
    main()