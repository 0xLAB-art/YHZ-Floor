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
    # All messages are XORed with the same key
    # If we have plaintext P_i at position j for message i, and ciphertext C_i[j]
    # Then key[j] = P_i[j] XOR C_i[j]
    # Once we have key[j], we can decrypt any message at position j
    
    # Build the key from known plaintexts
    key = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_hex = kp['data']
        plaintext = bytes.fromhex(plaintext_hex)
        
        ciphertext = ct_bytes[msg_idx]
        
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            c_byte = ciphertext[pos]
            key_byte = p_byte ^ c_byte
            key[pos] = key_byte
    
    # Now decrypt the target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ct_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in key:
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ key[pos]
            plaintext_bytes.append(p_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
