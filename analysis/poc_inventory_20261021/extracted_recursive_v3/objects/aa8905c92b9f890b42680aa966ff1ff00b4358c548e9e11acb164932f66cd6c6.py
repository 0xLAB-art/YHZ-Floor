import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_data[msg_idx] = bytes.fromhex(ct['data'])
    
    # Build keystream from known plaintexts
    # For stream cipher: ciphertext XOR plaintext = keystream
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = bytes.fromhex(kp['data'])
        ct_bytes = ct_data[msg_idx]
        
        for i, pt_byte in enumerate(pt_bytes):
            pos = offset + i
            ct_byte = ct_bytes[pos]
            ks_byte = ct_byte ^ pt_byte
            keystream[pos] = ks_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_data[target_msg_idx]
    plaintext_bytes = bytearray()
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = target_ct[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Should not happen if all keystream bytes are known
            plaintext_bytes.append(0)
    
    plaintext_hex = plaintext_bytes.hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()