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
    # XOR property: C_i = M_i XOR K, so C_i XOR C_j = M_i XOR M_j
    # If we know M_i at position p, we can find K at position p: K[p] = C_i[p] XOR M_i[p]
    # Then we can decrypt any other message: M_j[p] = C_j[p] XOR K[p]
    
    # Build the keystream
    keystream = {}
    
    # Process known plaintexts to extract keystream bytes
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        ct = ct_bytes[msg_idx]
        
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(ct):
                key_byte = ct[pos] ^ pt_byte
                keystream[pos] = key_byte
    
    # Now decrypt the target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Should not happen if we have enough known plaintexts
            plaintext.append(0)
    
    plaintext_hex = bytes(plaintext).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()