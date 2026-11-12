import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse input
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(bytes.fromhex(ct['data']))
    
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Determine keystream length needed
    max_pos = target['offset'] + target['length']
    keystream = [None] * max_pos
    
    # Recover keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        ciphertext = ciphertexts[msg_idx]
        
        # XOR to get keystream: K = P ⊕ C
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = p_byte ^ c_byte
                keystream[pos] = k_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    target_ciphertext = ciphertexts[target_msg_idx]
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext.append(p_byte)
        else:
            # If we don't have keystream at this position, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
