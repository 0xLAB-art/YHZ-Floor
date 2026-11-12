import json
import sys

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ciphertext_data = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ciphertext_data[msg_idx] = hex_to_bytes(ct['data'])
    
    # Recover keystream from known plaintexts
    # keystream[position] = ciphertext[position] XOR plaintext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        ciphertext = ciphertext_data[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            position = offset + i
            ct_byte = ciphertext[position]
            key_byte = ct_byte ^ pt_byte
            
            # Store or verify consistency
            if position in keystream:
                # Verify consistency (should always match in a valid instance)
                assert keystream[position] == key_byte
            else:
                keystream[position] = key_byte
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_data[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        position = target_offset + i
        ct_byte = target_ciphertext[position]
        
        if position in keystream:
            pt_byte = ct_byte ^ keystream[position]
            plaintext_bytes.append(pt_byte)
        else:
            # Should not happen if we have enough known plaintexts
            raise ValueError(f"Missing keystream at position {position}")
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()