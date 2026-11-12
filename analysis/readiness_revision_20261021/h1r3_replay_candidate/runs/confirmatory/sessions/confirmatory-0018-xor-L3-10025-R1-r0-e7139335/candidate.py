import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a map of ciphertext data by message_index
    ciphertext_map = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        data = bytes.fromhex(ct['data'])
        ciphertext_map[msg_idx] = data
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        if msg_idx in ciphertext_map:
            ciphertext = ciphertext_map[msg_idx]
            
            # Recover keystream: keystream = plaintext XOR ciphertext
            for i, p_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    c_byte = ciphertext[pos]
                    k_byte = p_byte ^ c_byte
                    keystream[pos] = k_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ciphertext_map:
        # This shouldn't happen based on the problem
        result = {'plaintext': '00' * target_length}
    else:
        target_ciphertext = ciphertext_map[target_msg_idx]
        plaintext_bytes = []
        
        for i in range(target_length):
            pos = target_offset + i
            if pos in keystream and pos < len(target_ciphertext):
                # Decrypt: plaintext = ciphertext XOR keystream
                p_byte = target_ciphertext[pos] ^ keystream[pos]
                plaintext_bytes.append(p_byte)
            else:
                # If we don't have keystream at this position, use 0x00
                # (shouldn't happen if problem is solvable)
                plaintext_bytes.append(0x00)
        
        plaintext_hex = bytes(plaintext_bytes).hex()
        result = {'plaintext': plaintext_hex}
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
