import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ciphertext_bytes = []
    for ct in ciphertexts:
        ciphertext_bytes.append(bytes.fromhex(ct['data']))
    
    # Recover keystream using known plaintexts
    # We need keystream for target positions
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Initialize keystream as None values
    max_len = max(len(ct) for ct in ciphertext_bytes)
    keystream = [None] * max_len
    
    # Recover keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_hex = kp['data']
        plaintext_bytes = bytes.fromhex(plaintext_hex)
        
        # XOR with ciphertext to get keystream
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertext_bytes[msg_idx][pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target using recovered keystream
    target_ciphertext = ciphertext_bytes[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if keystream[pos] is not None:
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream at this position, we have a problem
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
