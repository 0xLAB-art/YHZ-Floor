import sys
import json

def hex_to_bytes(h):
    return bytes.fromhex(h)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream from known plaintexts
    # keystream[position] = plaintext[position] XOR ciphertext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        ciphertext = ct_bytes[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertext[pos]
            ks_byte = pt_byte ^ ct_byte
            keystream[pos] = ks_byte
    
    # Now decrypt the target message using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ct_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            # But just in case, we'd need more sophisticated cryptanalysis
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
