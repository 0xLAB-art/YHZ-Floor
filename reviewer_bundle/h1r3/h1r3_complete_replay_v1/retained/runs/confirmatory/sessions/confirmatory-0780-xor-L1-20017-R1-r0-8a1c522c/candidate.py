import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
                   for ct in instance['ciphertexts']}
    known_plaintexts = {kp['message_index']: {
                            'offset': kp['offset'],
                            'data': hex_to_bytes(kp['data'])
                        } for kp in instance['known_plaintexts']}
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find a known plaintext we can use to recover the key
    for known_idx, known_info in known_plaintexts.items():
        known_offset = known_info['offset']
        known_data = known_info['data']
        
        # Get corresponding ciphertext
        if known_idx not in ciphertexts:
            continue
            
        ciphertext_known = ciphertexts[known_idx]
        
        # Extract the key from this known plaintext/ciphertext pair
        # K = P ⊕ C
        key_segment = xor_bytes(
            known_data,
            ciphertext_known[known_offset:known_offset + len(known_data)]
        )
        
        # Now use this key to decrypt the target
        if target_msg_idx in ciphertexts:
            ciphertext_target = ciphertexts[target_msg_idx]
            
            # The key we recovered starts at known_offset
            # We need it at target_offset
            # Assuming the key is reused at the same positions
            key_offset = known_offset
            
            if target_offset == key_offset:
                # Direct use
                plaintext = xor_bytes(
                    ciphertext_target[target_offset:target_offset + target_length],
                    key_segment[:target_length]
                )
                
                result = {
                    "plaintext": bytes_to_hex(plaintext)
                }
                print(json.dumps(result))
                return
    
    # Fallback: empty result (should not reach here with valid input)
    result = {"plaintext": "00" * target_length}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
