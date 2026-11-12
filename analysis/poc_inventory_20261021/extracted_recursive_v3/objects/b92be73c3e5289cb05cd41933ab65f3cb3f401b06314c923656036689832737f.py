import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Find the maximum length to determine keystream size
    max_len = max(len(ct) for ct in ct_bytes.values())
    
    # Initialize keystream as None for each position
    keystream = [None] * max_len
    
    # Extract keystream from known plaintexts
    # keystream[i] = ciphertext[i] XOR plaintext[i]
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        ct = ct_bytes[msg_idx]
        
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(ct):
                ks_byte = ct[pos] ^ pt_byte
                if keystream[pos] is None:
                    keystream[pos] = ks_byte
                elif keystream[pos] != ks_byte:
                    # Inconsistency - shouldn't happen with correct data
                    pass
    
    # Now decrypt the target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()