import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # XOR of two ciphertexts gives XOR of their plaintexts
    # If we know one plaintext, we can recover the keystream
    
    keystream = {}
    
    # Extract keystream bytes from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct_bytes[msg_idx]):
                # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
                key_byte = ct_bytes[msg_idx][pos] ^ pt_byte
                keystream[pos] = key_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(ct_bytes[target_msg_idx]):
            # plaintext[pos] = ciphertext[pos] XOR keystream[pos]
            pt_byte = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            plaintext.append(0)
    
    result = bytes(plaintext).hex()
    print(json.dumps({"plaintext": result}))

if __name__ == '__main__':
    main()