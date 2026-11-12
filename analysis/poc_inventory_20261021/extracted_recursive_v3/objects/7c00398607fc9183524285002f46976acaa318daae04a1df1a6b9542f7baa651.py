import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts from hex to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build keystream knowledge from known plaintexts
    # keystream[offset] = byte value
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_hex = kp['data']
        plaintext_bytes = bytes.fromhex(plaintext_hex)
        
        # XOR: ciphertext = plaintext XOR keystream
        # Therefore: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ct_bytes[msg_idx][pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Now recover the target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We know the keystream at this position
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            result_bytes.append(pt_byte)
        else:
            # We don't have keystream knowledge at this position
            # This shouldn't happen if the instance is solvable
            result_bytes.append(0)
    
    plaintext_hex = bytes(result_bytes).hex()
    
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()