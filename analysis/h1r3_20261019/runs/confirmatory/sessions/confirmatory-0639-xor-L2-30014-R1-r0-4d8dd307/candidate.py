import sys
import json

def hex_to_bytes(h):
    return bytes.fromhex(h)

def bytes_to_hex(b):
    return b.hex()

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        ciphertexts[idx] = hex_to_bytes(ct['data'])
    
    # Determine keystream length from ciphertexts
    keystream_length = len(ciphertexts[0])
    
    # Initialize keystream as unknown
    keystream = [None] * keystream_length
    
    # Process known plaintexts to recover keystream
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        ciphertext = ciphertexts[msg_idx]
        
        # For each byte in the known plaintext
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            c_byte = ciphertext[pos]
            k_byte = c_byte ^ p_byte
            
            # Store keystream byte (verify consistency if already known)
            if keystream[pos] is not None and keystream[pos] != k_byte:
                # Inconsistency - shouldn't happen with valid data
                pass
            keystream[pos] = k_byte
    
    # Extract target range
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Decrypt target message
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if keystream[pos] is not None:
            # We know the keystream at this position
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # Keystream unknown at this position - shouldn't happen if solvable
            # Use 0 as fallback
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
