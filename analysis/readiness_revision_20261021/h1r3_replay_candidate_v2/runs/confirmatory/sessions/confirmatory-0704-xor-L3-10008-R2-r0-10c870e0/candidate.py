import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Determine keystream length (all ciphertexts should be same length)
    keystream_len = len(ciphertexts[0])
    
    # Initialize keystream as None (unknown bytes)
    keystream = [None] * keystream_len
    
    # Extract keystream from known plaintexts
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        # Recover keystream: K = P ⊕ C
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            c_byte = ciphertexts[msg_idx][pos]
            k_byte = p_byte ^ c_byte
            
            # Store keystream byte (verify consistency if already known)
            if keystream[pos] is not None:
                assert keystream[pos] == k_byte, f"Keystream mismatch at position {pos}"
            keystream[pos] = k_byte
    
    # Decrypt target
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        
        # Check if we have keystream for this position
        if keystream[pos] is None:
            # This shouldn't happen if we have enough known plaintexts
            # But if it does, we can't decrypt this byte
            raise ValueError(f"Missing keystream at position {pos}")
        
        c_byte = ciphertexts[target_msg_idx][pos]
        p_byte = c_byte ^ keystream[pos]
        plaintext_bytes.append(p_byte)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
