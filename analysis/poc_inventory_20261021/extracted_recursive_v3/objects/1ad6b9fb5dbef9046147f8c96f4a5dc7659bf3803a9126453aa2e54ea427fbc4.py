import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # We can recover the keystream at positions where we have known plaintexts
    # keystream[i] = ciphertext[i] XOR plaintext[i]
    
    # Find the maximum length needed
    max_len = 0
    for ct in ct_bytes:
        max_len = max(max_len, len(ct))
    
    # Initialize keystream as None values
    keystream = [None] * max_len
    
    # Recover keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = bytes.fromhex(kp['data'])
        
        ciphertext = ct_bytes[msg_idx]
        
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                k_byte = ciphertext[pos] ^ p_byte
                
                # Verify consistency if we already have this keystream byte
                if keystream[pos] is not None:
                    if keystream[pos] != k_byte:
                        # Inconsistency - but we'll trust the new value
                        pass
                keystream[pos] = k_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            p_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # We don't have the keystream for this position
            # This shouldn't happen if the instance is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()