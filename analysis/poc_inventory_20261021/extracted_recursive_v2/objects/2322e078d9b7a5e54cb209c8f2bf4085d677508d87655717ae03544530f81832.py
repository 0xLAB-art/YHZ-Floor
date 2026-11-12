import json
import sys

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        ct_data[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream from known plaintexts
    # keystream[position] = plaintext[position] XOR ciphertext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        ciphertext = ct_data[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertext[pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    target_ciphertext = ct_data[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Should not happen if we have enough known plaintexts
            raise ValueError(f"Keystream not recovered at position {pos}")
    
    plaintext_hex = bytes_to_hex(bytes(plaintext_bytes))
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
