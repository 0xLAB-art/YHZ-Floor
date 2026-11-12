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
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_data[msg_idx] = hex_to_bytes(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        ciphertext = ct_data[msg_idx]
        
        # Extract keystream: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(plaintext_bytes):
            position = offset + i
            ct_byte = ciphertext[position]
            ks_byte = pt_byte ^ ct_byte
            keystream[position] = ks_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ct_data[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        position = target_offset + i
        if position in keystream:
            ct_byte = target_ciphertext[position]
            pt_byte = ct_byte ^ keystream[position]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            raise ValueError(f"Missing keystream at position {position}")
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
