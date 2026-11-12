import json
import sys

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
    
    # Recover keystream from known plaintexts
    # keystream[position] will store the recovered keystream byte at that position
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        ciphertext = ciphertext_map[msg_idx]
        
        # For each byte in this known plaintext, recover the keystream
        for i, pt_byte in enumerate(plaintext_bytes):
            position = offset + i
            ct_byte = ciphertext[position]
            ks_byte = ct_byte ^ pt_byte
            keystream[position] = ks_byte
    
    # Now decrypt the target message using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_map[target_msg_idx]
    
    plaintext_bytes = bytearray()
    for i in range(target_length):
        position = target_offset + i
        if position in keystream:
            ct_byte = target_ciphertext[position]
            pt_byte = ct_byte ^ keystream[position]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            # But handle it gracefully
            plaintext_bytes.append(0)
    
    result = {
        "plaintext": bytes_to_hex(plaintext_bytes)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()