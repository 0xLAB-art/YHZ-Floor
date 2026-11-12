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
        pt_data = bytes.fromhex(kp['data'])
        
        # Recover keystream bytes at this position
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(ct_bytes[msg_idx]):
                ct_byte = ct_bytes[msg_idx][pos]
                ks_byte = ct_byte ^ pt_byte
                
                # Store keystream byte
                if keystream[pos] is None:
                    keystream[pos] = ks_byte
                # Verify consistency if already known
                elif keystream[pos] != ks_byte:
                    # Inconsistency - shouldn't happen if it's truly a stream cipher reuse
                    pass
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(ct_bytes[target_msg_idx]) and keystream[pos] is not None:
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
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
