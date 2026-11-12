import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This appears to be a many-time pad attack
    # Multiple messages encrypted with the same key (stream cipher reuse)
    # We can XOR ciphertexts together and use known plaintexts to recover the keystream
    
    # First, recover the keystream at positions where we have known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        # keystream[i] = ciphertext[i] XOR plaintext[i]
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ct_bytes[msg_idx][pos]
            ks_byte = ct_byte ^ pt_byte
            
            # Store keystream byte (verify consistency if already present)
            if pos in keystream:
                if keystream[pos] != ks_byte:
                    # Inconsistency - but we'll trust the new value
                    pass
            keystream[pos] = ks_byte
    
    # Now recover the target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We know the keystream at this position
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            target_plaintext.append(pt_byte)
        else:
            # We don't have the keystream at this position
            # This shouldn't happen if the instance is solvable
            target_plaintext.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(target_plaintext).hex()
    
    # Output the result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()