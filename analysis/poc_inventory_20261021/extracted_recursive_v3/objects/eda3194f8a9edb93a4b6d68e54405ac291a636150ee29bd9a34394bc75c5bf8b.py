import json
import sys

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        msg_idx = ct['message_index']
        ciphertexts[msg_idx] = hex_to_bytes(ct['data'])
    
    # Determine maximum length needed
    max_len = max(len(ct) for ct in ciphertexts.values())
    
    # Initialize keystream recovery (None means unknown)
    keystream = [None] * max_len
    
    # Process known plaintexts to recover keystream
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        ciphertext = ciphertexts[msg_idx]
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                key_byte = pt_byte ^ ciphertext[pos]
                keystream[pos] = key_byte
    
    # Extract target information
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Decrypt target
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()