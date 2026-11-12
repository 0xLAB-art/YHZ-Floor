import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a map of ciphertext data by message_index
    ciphertext_map = {}
    for ct in ciphertexts:
        ciphertext_map[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    # keystream[position] = ciphertext[position] XOR plaintext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_data = hex_to_bytes(kp['data'])
        ciphertext_data = ciphertext_map[msg_idx]
        
        # XOR to recover keystream at these positions
        for i, pt_byte in enumerate(plaintext_data):
            pos = offset + i
            ct_byte = ciphertext_data[pos]
            keystream[pos] = ct_byte ^ pt_byte
    
    # Now decrypt the target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_map[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: plaintext = ciphertext XOR keystream
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes_to_hex(bytes(plaintext_bytes))
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()