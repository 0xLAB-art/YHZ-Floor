import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert all ciphertext hex strings to byte arrays
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This appears to be a many-time pad attack (stream cipher reuse)
    # If the same keystream is used for multiple messages, we can exploit known plaintexts
    
    # Build keystream from known plaintexts
    # keystream[offset] = ciphertext[offset] XOR plaintext[offset]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        ciphertext = ct_bytes[msg_idx]
        
        # Extract keystream bytes at this offset
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                key_byte = ciphertext[pos] ^ pt_byte
                keystream[pos] = key_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ct_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have the keystream at this position, we can't decrypt
            # This shouldn't happen if the challenge is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
