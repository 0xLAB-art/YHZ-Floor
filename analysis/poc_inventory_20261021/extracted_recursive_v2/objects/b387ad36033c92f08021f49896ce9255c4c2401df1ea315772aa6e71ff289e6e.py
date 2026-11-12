import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # Determine the maximum length we need
    max_len = target['offset'] + target['length']
    
    # Recover keystream bytes where we have known plaintexts
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        # For each byte in this known plaintext
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(ct_bytes[msg_idx]):
                ct_byte = ct_bytes[msg_idx][pos]
                ks_byte = ct_byte ^ pt_byte
                
                # Store keystream byte if we don't have it yet
                if keystream[pos] is None:
                    keystream[pos] = ks_byte
                # Verify consistency if we already have it
                elif keystream[pos] != ks_byte:
                    # Inconsistent - but we'll trust the first one
                    pass
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if keystream[pos] is not None and pos < len(ct_bytes[target_msg_idx]):
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt
            # This shouldn't happen if the problem is well-formed
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
