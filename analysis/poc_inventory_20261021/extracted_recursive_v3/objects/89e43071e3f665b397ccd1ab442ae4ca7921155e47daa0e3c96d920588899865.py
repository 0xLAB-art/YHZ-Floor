import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ciphertexts_bytes = []
    for ct in ciphertexts:
        ciphertexts_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # We have multiple messages encrypted with the same key (stream cipher reuse)
    # XOR properties: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can find P2
    
    # Build a keystream from known plaintexts
    max_length = max(len(ct) for ct in ciphertexts_bytes)
    keystream = [None] * max_length
    
    # For each known plaintext, recover the keystream at those positions
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        ciphertext = ciphertexts_bytes[msg_idx]
        
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                key_byte = ciphertext[pos] ^ p_byte
                if keystream[pos] is None:
                    keystream[pos] = key_byte
                elif keystream[pos] != key_byte:
                    # Inconsistency check - should not happen if data is correct
                    pass
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertexts_bytes[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have the keystream at this position, we need to guess or derive it
            # This shouldn't happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()