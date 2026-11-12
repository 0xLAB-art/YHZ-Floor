import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # Find the maximum length we need
    max_len = max(len(ct) for ct in ct_bytes)
    
    # Initialize keystream as None (unknown)
    keystream = [None] * max_len
    
    # Recover keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        # Get corresponding ciphertext
        ct = ct_bytes[msg_idx]
        
        # Recover keystream bytes at this position
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(ct):
                ks_byte = ct[pos] ^ pt_byte
                # Store keystream byte (should be consistent if we see it multiple times)
                if keystream[pos] is None:
                    keystream[pos] = ks_byte
                else:
                    # Verify consistency
                    assert keystream[pos] == ks_byte, f"Keystream mismatch at position {pos}"
    
    # Now decrypt the target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            raise ValueError(f"Missing keystream at position {pos}")
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
