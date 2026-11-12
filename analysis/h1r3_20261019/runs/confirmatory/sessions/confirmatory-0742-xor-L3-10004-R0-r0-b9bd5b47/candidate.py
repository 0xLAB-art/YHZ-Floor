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
    # XOR reuse: if C1 = P1 ⊕ K and C2 = P2 ⊕ K, then C1 ⊕ C2 = P1 ⊕ P2
    # With known plaintexts, we can recover the key at those positions
    
    # Recover key bytes at known positions
    key = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ct_bytes[msg_idx][pos]
            key_byte = ct_byte ^ pt_byte
            
            # Store key byte (verify consistency if already exists)
            if pos in key:
                if key[pos] != key_byte:
                    # Inconsistency - should not happen with valid data
                    pass
            else:
                key[pos] = key_byte
    
    # Now decrypt the target using recovered key
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in key:
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ key[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Key not recovered at this position - try to infer or fail
            # For now, we'll use 0x00 as placeholder (should not happen if enough knowns)
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
