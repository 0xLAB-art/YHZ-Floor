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
    
    # Build a map of ciphertexts by message_index
    ciphertext_map = {}
    for ct in ciphertexts:
        ciphertext_map[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        ciphertext_bytes = ciphertext_map[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertext_bytes[pos]
            ks_byte = pt_byte ^ ct_byte
            keystream[pos] = ks_byte
    
    # Decrypt the target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_map[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Should not happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes_to_hex(bytes(plaintext_bytes))
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
