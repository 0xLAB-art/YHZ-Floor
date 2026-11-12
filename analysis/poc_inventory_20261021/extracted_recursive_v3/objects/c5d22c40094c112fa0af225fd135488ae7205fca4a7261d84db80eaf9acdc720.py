import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_dict = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_dict[msg_idx] = bytes.fromhex(ct['data'])
    
    # Recover keystream from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = bytes.fromhex(kp['data'])
        ciphertext = ct_dict[msg_idx]
        
        # keystream[pos] = plaintext[pos] XOR ciphertext[pos]
        for i, pt_byte in enumerate(plaintext):
            pos = offset + i
            ct_byte = ciphertext[pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    target_ct = ct_dict[target_msg_idx]
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: plaintext = ciphertext XOR keystream
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # If we don't have the keystream at this position, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext.append(0)
    
    # Convert to hex
    result = bytes(plaintext).hex()
    
    # Output JSON
    output = {"plaintext": result}
    print(json.dumps(output))

if __name__ == '__main__':
    main()