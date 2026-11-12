import json
import sys

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
    
    # Build a map of ciphertext by message_index
    cipher_map = {}
    for ct in ciphertexts:
        cipher_map[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        ciphertext = cipher_map[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                key_byte = ciphertext[pos] ^ pt_byte
                keystream[pos] = key_byte
    
    # Decrypt the target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    target_ciphertext = cipher_map[target_msg_idx]
    
    plaintext_bytes = bytearray()
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    result = {
        "plaintext": bytes_to_hex(plaintext_bytes)
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()
