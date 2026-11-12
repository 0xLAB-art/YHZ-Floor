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
    
    # Convert ciphertexts to bytes
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        ciphertext = ct_map[msg_idx]
        
        # XOR plaintext with ciphertext to get keystream
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertext[pos]
            ks_byte = pt_byte ^ ct_byte
            keystream[pos] = ks_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ct_map[target_msg_idx]
    plaintext_bytes = bytearray()
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We have the keystream byte, decrypt
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Unknown keystream byte - this shouldn't happen if we have enough known plaintexts
            # Try to infer or fail gracefully
            plaintext_bytes.append(0)
    
    result = {
        "plaintext": bytes_to_hex(plaintext_bytes)
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
