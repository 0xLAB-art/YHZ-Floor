import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse input
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        data = bytes.fromhex(ct['data'])
        ciphertexts[idx] = data
    
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Recover keystream from known plaintexts
    # keystream[position] = ciphertext[position] XOR plaintext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        if msg_idx not in ciphertexts:
            continue
            
        ciphertext = ciphertexts[msg_idx]
        
        # Recover keystream for each byte
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                ct_byte = ciphertext[pos]
                ks_byte = ct_byte ^ pt_byte
                keystream[pos] = ks_byte
    
    # Decrypt target using recovered keystream
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
