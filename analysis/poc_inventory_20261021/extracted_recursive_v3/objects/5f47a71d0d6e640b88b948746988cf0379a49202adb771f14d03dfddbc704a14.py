import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build keystream from known plaintexts
    # For stream cipher: ciphertext = plaintext XOR keystream
    # So: keystream = plaintext XOR ciphertext
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        ct = ct_bytes[msg_idx]
        
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            ct_byte = ct[pos]
            ks_byte = pt_byte ^ ct_byte
            keystream[pos] = ks_byte
    
    # Extract target plaintext using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = target_ct[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Should not happen if keystream is fully recovered
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()