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
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert all ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(hex_to_bytes(ct['data']))
    
    # Recover keystream bytes from known plaintexts
    # keystream[position] = ciphertext[position] XOR plaintext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        plaintext_data = hex_to_bytes(kp['data'])
        message_index = kp['message_index']
        offset = kp['offset']
        
        ciphertext = ct_bytes[message_index]
        
        # For each byte in the known plaintext
        for i, pt_byte in enumerate(plaintext_data):
            position = offset + i
            ct_byte = ciphertext[position]
            
            # Recover keystream byte: K = C XOR P
            keystream[position] = ct_byte ^ pt_byte
    
    # Now decrypt the target using the recovered keystream
    target_message_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ct_bytes[target_message_index]
    
    plaintext_bytes = []
    for i in range(target_length):
        position = target_offset + i
        
        if position in keystream:
            # Decrypt: P = C XOR K
            ct_byte = target_ciphertext[position]
            pt_byte = ct_byte ^ keystream[position]
            plaintext_bytes.append(pt_byte)
        else:
            # We don't have this keystream byte - this shouldn't happen
            # if the problem is solvable, but handle gracefully
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes_to_hex(bytes(plaintext_bytes))
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()