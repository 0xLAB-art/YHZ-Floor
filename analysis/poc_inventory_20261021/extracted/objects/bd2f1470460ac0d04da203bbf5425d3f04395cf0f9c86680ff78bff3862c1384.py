import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This appears to be a many-time pad attack (stream cipher reuse)
    # When the same keystream is reused: C1 XOR C2 = P1 XOR P2
    # Given known plaintexts, we can recover keystream bytes
    
    # Build keystream for each message position
    max_len = max(len(ct) for ct in ct_bytes)
    keystream = {}
    
    # Extract keystream bytes from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        # For each byte in this known plaintext
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct_bytes[msg_idx]):
                # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
                ks_byte = ct_bytes[msg_idx][pos] ^ pt_byte
                keystream[pos] = ks_byte
    
    # Now recover the target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: plaintext = ciphertext XOR keystream
            pt_byte = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
            result.append(pt_byte)
        else:
            # If we don't have the keystream byte, we need to infer it
            # This shouldn't happen with enough known plaintexts
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()
