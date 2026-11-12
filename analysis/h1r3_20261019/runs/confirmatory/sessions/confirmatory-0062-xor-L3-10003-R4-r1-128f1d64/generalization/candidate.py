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
    
    # Recover keystream using known plaintexts
    # keystream[position] = ciphertext[position] XOR plaintext[position]
    max_len = max(len(ct) for ct in ct_bytes)
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        ciphertext = ct_bytes[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                # Recover keystream byte
                ks_byte = ciphertext[pos] ^ pt_byte
                
                # Store if not already known, or verify consistency
                if keystream[pos] is None:
                    keystream[pos] = ks_byte
                elif keystream[pos] != ks_byte:
                    # Inconsistency - shouldn't happen with correct data
                    pass
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ct_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Should not happen if we have complete keystream coverage
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
