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
    
    # Recover keystream from known plaintexts
    # Initialize keystream as None values
    target_offset = target['offset']
    target_length = target['length']
    keystream = [None] * (target_offset + target_length)
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        # Recover keystream bytes
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(keystream):
                # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
                ct_byte = ct_bytes[msg_idx][pos]
                ks_byte = ct_byte ^ pt_byte
                keystream[pos] = ks_byte
    
    # Decrypt target ciphertext
    target_msg_idx = target['message_index']
    target_ct = ct_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if keystream[pos] is not None:
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if we have complete coverage
            # But just in case, we'd need to use crib-dragging or other techniques
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
