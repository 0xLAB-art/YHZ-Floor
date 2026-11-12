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
    # XOR of two ciphertexts eliminates the keystream: C1 ⊕ C2 = P1 ⊕ P2
    # Given known plaintexts, we can recover keystream bytes
    
    # Recover keystream
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            c_byte = ct_bytes[msg_idx][pos]
            k_byte = c_byte ^ p_byte
            
            # Store keystream byte
            if pos not in keystream:
                keystream[pos] = k_byte
            else:
                # Verify consistency
                assert keystream[pos] == k_byte, f"Inconsistent keystream at position {pos}"
    
    # Decrypt target using recovered keystream
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
            # This shouldn't happen if we have enough known plaintexts
            raise ValueError(f"Keystream byte at position {pos} not recovered")
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
