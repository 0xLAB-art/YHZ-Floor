import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ciphertext_bytes = []
    for ct in ciphertexts:
        ciphertext_bytes.append(bytes.fromhex(ct['data']))
    
    # Determine the maximum length needed for keystream
    max_len = 0
    for ct in ciphertext_bytes:
        max_len = max(max_len, len(ct))
    
    # Initialize keystream as None for unknown bytes
    keystream = [None] * max_len
    
    # Recover keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        ciphertext = ciphertext_bytes[msg_idx]
        
        # For each byte in this known plaintext
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = p_byte ^ c_byte
                
                # Store in keystream (check consistency if already set)
                if keystream[pos] is not None:
                    if keystream[pos] != k_byte:
                        # Inconsistency - shouldn't happen with valid data
                        pass
                else:
                    keystream[pos] = k_byte
    
    # Decrypt the target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # Unknown keystream byte - this shouldn't happen if we have enough info
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()