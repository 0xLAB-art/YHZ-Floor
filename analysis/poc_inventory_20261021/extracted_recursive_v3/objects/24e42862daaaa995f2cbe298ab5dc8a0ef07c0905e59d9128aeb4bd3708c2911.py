import sys
import json

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Extract target information
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Parse known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = hex_to_bytes(kp['data'])
        if msg_idx not in known_plaintexts:
            known_plaintexts[msg_idx] = {}
        known_plaintexts[msg_idx][offset] = data
    
    # Find a known plaintext that overlaps with our target
    # Strategy: Use known plaintext to recover the keystream, then decrypt target
    
    # Get the target ciphertext
    target_ciphertext = ciphertexts[target_msg_idx]
    target_ciphertext_segment = target_ciphertext[target_offset:target_offset + target_length]
    
    # Find a known plaintext we can use to recover the key
    # Look for known plaintext at the same position in a different message
    for kp_msg_idx, kp_data_dict in known_plaintexts.items():
        for kp_offset, kp_plaintext in kp_data_dict.items():
            # Check if we have the ciphertext for this known plaintext
            if kp_msg_idx in ciphertexts:
                kp_ciphertext = ciphertexts[kp_msg_idx]
                
                # Extract the relevant segment
                kp_ct_segment = kp_ciphertext[kp_offset:kp_offset + len(kp_plaintext)]
                
                # Recover the keystream for this segment
                keystream = xor_bytes(kp_plaintext, kp_ct_segment)
                
                # Check if this keystream overlaps with our target
                # Assuming stream cipher reuses key at same positions
                if kp_offset <= target_offset < kp_offset + len(keystream):
                    # We have overlap
                    key_start_in_keystream = target_offset - kp_offset
                    key_segment = keystream[key_start_in_keystream:key_start_in_keystream + target_length]
                    
                    # Decrypt target
                    plaintext = xor_bytes(target_ciphertext_segment, key_segment)
                    result = {"plaintext": bytes_to_hex(plaintext)}
                    print(json.dumps(result))
                    return
                
                # If the keystream starts at the same offset as target
                if kp_offset == target_offset:
                    key_segment = keystream[:target_length]
                    plaintext = xor_bytes(target_ciphertext_segment, key_segment)
                    result = {"plaintext": bytes_to_hex(plaintext)}
                    print(json.dumps(result))
                    return
    
    # If no direct match, assume the key is reused across all messages at same positions
    # This is the classic stream cipher key reuse scenario
    for kp_msg_idx, kp_data_dict in known_plaintexts.items():
        if kp_msg_idx in ciphertexts:
            for kp_offset, kp_plaintext in kp_data_dict.items():
                kp_ciphertext = ciphertexts[kp_msg_idx]
                kp_ct_segment = kp_ciphertext[kp_offset:kp_offset + len(kp_plaintext)]
                
                # Recover keystream at this offset
                keystream = xor_bytes(kp_plaintext, kp_ct_segment)
                
                # Use this keystream to decrypt the target at the same offset
                target_key = keystream[0:min(len(keystream), target_length)]
                target_pt_segment = xor_bytes(target_ciphertext_segment[:len(target_key)], target_key)
                
                if len(target_pt_segment) == target_length:
                    result = {"plaintext": bytes_to_hex(target_pt_segment)}
                    print(json.dumps(result))
                    return

if __name__ == "__main__":
    main()