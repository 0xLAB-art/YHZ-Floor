import json
import sys

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ct_map = {}
    for ct_obj in ciphertexts:
        msg_idx = ct_obj['message_index']
        ct_map[msg_idx] = hex_to_bytes(ct_obj['data'])
    
    # Recover keystream from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        ciphertext = ct_map[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertext[pos]
            ks_byte = ct_byte ^ pt_byte
            keystream[pos] = ks_byte
    
    # Decrypt target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ct_map[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If keystream byte not recovered, we have a problem
            # For now, use 0x00 as placeholder (shouldn't happen with valid input)
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
