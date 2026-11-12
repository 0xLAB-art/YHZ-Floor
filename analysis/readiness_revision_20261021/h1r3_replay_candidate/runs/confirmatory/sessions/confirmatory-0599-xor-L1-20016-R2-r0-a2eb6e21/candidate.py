import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse input
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts[ct['message_index']] = data
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts[kp['message_index']] = {
            'data': data,
            'offset': kp['offset']
        }
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Stream cipher reuse attack
    # If C0 = P0 ⊕ K and C1 = P1 ⊕ K (same keystream K)
    # Then C0 ⊕ P0 = K, and P1 = C1 ⊕ K = C1 ⊕ C0 ⊕ P0
    
    # Find a known plaintext we can use
    for known_idx, known_data in known_plaintexts.items():
        known_plaintext = known_data['data']
        known_offset = known_data['offset']
        
        # Get the corresponding ciphertext
        ct_known = ciphertexts[known_idx]
        ct_target = ciphertexts[target_msg_idx]
        
        # Extract keystream from known plaintext/ciphertext pair
        # K[i] = P_known[i] ⊕ C_known[i]
        keystream_start = known_offset
        keystream_end = known_offset + len(known_plaintext)
        
        # Check if this covers our target range
        if keystream_start <= target_offset and keystream_end >= target_offset + target_length:
            # We can recover the target plaintext
            result = bytearray()
            
            for i in range(target_length):
                target_pos = target_offset + i
                known_pos = target_pos - known_offset
                
                # K[target_pos] = P_known[known_pos] ⊕ C_known[target_pos]
                k = known_plaintext[known_pos] ^ ct_known[target_pos]
                
                # P_target[i] = C_target[target_pos] ⊕ K[target_pos]
                p = ct_target[target_pos] ^ k
                result.append(p)
            
            # Output as lowercase hex
            plaintext_hex = result.hex()
            print(json.dumps({"plaintext": plaintext_hex}))
            return
    
    # If we get here, we couldn't solve it with available known plaintexts
    print(json.dumps({"plaintext": "00" * target_length}))

if __name__ == '__main__':
    main()
