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
    
    # This is a many-time pad attack (stream cipher key reuse)
    # When the same key is used multiple times: C_i = P_i XOR K
    # If we know P_i at some position, we can find K at that position: K = C_i XOR P_i
    # Then we can decrypt any other ciphertext at that position: P_j = C_j XOR K
    
    # Build keystream from known plaintexts
    max_len = max(len(ct) for ct in ct_bytes)
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = bytes.fromhex(kp['data'])
        
        for i, pt_byte in enumerate(pt_bytes):
            pos = offset + i
            if pos < len(ct_bytes[msg_idx]):
                # Recover keystream byte: K[pos] = C[msg_idx][pos] XOR P[pos]
                key_byte = ct_bytes[msg_idx][pos] ^ pt_byte
                
                # Store or verify consistency
                if keystream[pos] is None:
                    keystream[pos] = key_byte
                elif keystream[pos] != key_byte:
                    # Inconsistency - shouldn't happen with correct data
                    pass
    
    # Now decrypt the target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(ct_bytes[target_msg_idx]) and keystream[pos] is not None:
            pt_byte = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have the keystream byte, we need to use crib-dragging
            # or other techniques, but with enough known plaintexts this shouldn't happen
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
