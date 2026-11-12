import sys
import json

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert all ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_bytes[msg_idx] = hex_to_bytes(ct['data'])
    
    # Recover keystream using known plaintexts
    # keystream[position] = plaintext[position] XOR ciphertext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = hex_to_bytes(kp['data'])
        
        # Get corresponding ciphertext bytes
        ct = ct_bytes[msg_idx]
        
        # Recover keystream at these positions
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            ct_byte = ct[pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Now decrypt the target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt using known keystream
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            # But handle it gracefully
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()