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
    
    # Build keystream from known plaintexts
    # keystream[position] = key byte at that position
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            # XOR: ciphertext[pos] = plaintext[pos] ^ key[pos]
            # So: key[pos] = ciphertext[pos] ^ plaintext[pos]
            ct_byte = ct_bytes[msg_idx][pos]
            key_byte = ct_byte ^ pt_byte
            keystream[pos] = key_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen if the instance is solvable
            plaintext.append(0)
    
    plaintext_hex = bytes(plaintext).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
