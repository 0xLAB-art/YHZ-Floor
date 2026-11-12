import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Create a map from message_index to ciphertext bytes
    cipher_map = {}
    for ct in ciphertexts:
        cipher_map[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream from known plaintexts
    # keystream[position] = plaintext XOR ciphertext
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        ciphertext_bytes = cipher_map[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertext_bytes[pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = cipher_map[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
