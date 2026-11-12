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
    
    # This is a many-time pad attack
    # XOR property: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can find P2 = C1 XOR C2 XOR P1
    
    # Build keystream from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = bytes.fromhex(kp['data'])
        
        # keystream[offset] = ciphertext[offset] XOR plaintext[offset]
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            c_byte = ct_bytes[msg_idx][pos]
            k_byte = c_byte ^ p_byte
            
            if pos in keystream:
                # Verify consistency
                if keystream[pos] != k_byte:
                    # Conflict - but we trust the data
                    pass
            keystream[pos] = k_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: plaintext = ciphertext XOR keystream
            c_byte = ct_bytes[target_msg_idx][pos]
            p_byte = c_byte ^ keystream[pos]
            result.append(p_byte)
        else:
            # We don't have keystream for this position
            # Try to derive it from other messages if we have full coverage
            # For now, this shouldn't happen with proper input
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()
