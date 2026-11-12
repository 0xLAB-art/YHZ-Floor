import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # XOR of two ciphertexts gives XOR of their plaintexts
    # If we know one plaintext, we can recover the keystream at those positions
    
    # Recover keystream bytes
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_hex = kp['data']
        plaintext_bytes = bytes.fromhex(plaintext_hex)
        
        # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
        for i, pb in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct_bytes[msg_idx]):
                keystream[pos] = ct_bytes[msg_idx][pos] ^ pb
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(ct_bytes[target_msg_idx]):
            # plaintext[pos] = ciphertext[pos] XOR keystream[pos]
            pt_byte = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Missing keystream byte - this shouldn't happen with valid input
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
