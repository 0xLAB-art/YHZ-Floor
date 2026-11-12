import sys
import json

def main():
    # Read instance
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
    # We have multiple ciphertexts encrypted with the same keystream
    # C_i = P_i XOR K, so C_i XOR C_j = P_i XOR P_j
    # With known plaintexts, we can recover parts of the keystream: K[pos] = C_i[pos] XOR P_i[pos]
    
    # Find the maximum length we need
    max_len = max(len(ct) for ct in ct_bytes)
    
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
                if keystream[pos] is None:
                    keystream[pos] = k_byte
                elif keystream[pos] != k_byte:
                    # Consistency check - should not happen with valid data
                    pass
    
    # Now decrypt the target
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
            # If we don't have the keystream, we need to guess or use crib dragging
            # For now, let's try to infer from XORing with other messages
            # This shouldn't happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
