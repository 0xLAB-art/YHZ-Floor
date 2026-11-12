import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    target = instance['target']
    ciphertexts = {ct['message_index']: ct['data'] for ct in instance['ciphertexts']}
    known_plaintexts = {kp['message_index']: {'offset': kp['offset'], 'data': kp['data']} 
                        for kp in instance['known_plaintexts']}
    
    # Convert hex strings to bytes
    ciphertexts_bytes = {idx: bytes.fromhex(data) for idx, data in ciphertexts.items()}
    known_plaintexts_bytes = {idx: {'offset': kp['offset'], 'data': bytes.fromhex(kp['data'])} 
                              for idx, kp in known_plaintexts.items()}
    
    # This is a stream cipher reuse attack
    # C0 = P0 XOR K
    # C1 = P1 XOR K
    # We know P0, so we can recover K at those positions: K = P0 XOR C0
    # Then we can recover P1: P1 = C1 XOR K
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find a known plaintext we can use
    for known_idx, known_data in known_plaintexts_bytes.items():
        known_offset = known_data['offset']
        known_plaintext = known_data['data']
        known_ciphertext = ciphertexts_bytes[known_idx]
        
        # Recover the keystream at the known positions
        keystream_start = known_offset
        keystream_end = known_offset + len(known_plaintext)
        
        keystream = bytes([p ^ c for p, c in zip(known_plaintext, 
                          known_ciphertext[keystream_start:keystream_end])])
        
        # Check if this covers our target
        if target_offset >= keystream_start and target_offset + target_length <= keystream_end:
            # We can decrypt the target
            target_ciphertext = ciphertexts_bytes[target_msg_idx]
            
            # Extract the relevant keystream portion
            key_offset = target_offset - keystream_start
            relevant_keystream = keystream[key_offset:key_offset + target_length]
            
            # Decrypt the target
            target_plaintext = bytes([c ^ k for c, k in 
                                     zip(target_ciphertext[target_offset:target_offset + target_length],
                                         relevant_keystream)])
            
            result = {
                "plaintext": target_plaintext.hex()
            }
            print(json.dumps(result))
            return
    
    # If we get here, we couldn't decrypt (shouldn't happen with valid input)
    result = {"plaintext": "00" * target_length}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
