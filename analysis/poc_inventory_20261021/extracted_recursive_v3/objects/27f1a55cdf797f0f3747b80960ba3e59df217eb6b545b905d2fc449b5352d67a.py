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
    
    # This appears to be a many-time pad attack
    # Multiple messages encrypted with the same keystream
    # We can recover the keystream at positions where we have known plaintext
    
    # Recover keystream bytes
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            c_byte = ct_bytes[msg_idx][pos]
            k_byte = c_byte ^ p_byte
            
            # Store keystream byte (should be consistent across all messages)
            if pos in keystream:
                # Verify consistency
                if keystream[pos] != k_byte:
                    # There might be an inconsistency, but let's trust the data
                    pass
            keystream[pos] = k_byte
    
    # Now decrypt the target message using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            c_byte = ct_bytes[target_msg_idx][pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # We don't have this keystream byte
            # This shouldn't happen if we have enough known plaintext
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()