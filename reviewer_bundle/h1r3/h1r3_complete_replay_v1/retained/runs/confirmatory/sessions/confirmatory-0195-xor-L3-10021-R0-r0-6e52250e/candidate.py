import json
import sys

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    cipher_bytes = []
    for ct in ciphertexts:
        cipher_bytes.append(bytes.fromhex(ct['data']))
    
    # Recover keystream bytes from known plaintexts
    # keystream[position] = ciphertext[message_index][position] ^ plaintext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_data = bytes.fromhex(kp['data'])
        
        for i, pt_byte in enumerate(plaintext_data):
            position = offset + i
            ct_byte = cipher_bytes[msg_idx][position]
            keystream[position] = ct_byte ^ pt_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        position = target_offset + i
        if position in keystream:
            ct_byte = cipher_bytes[target_msg_idx][position]
            pt_byte = ct_byte ^ keystream[position]
            plaintext.append(pt_byte)
        else:
            # This shouldn't happen if the instance is solvable
            # But handle gracefully
            plaintext.append(0)
    
    # Convert to hex string
    plaintext_hex = bytes(plaintext).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
