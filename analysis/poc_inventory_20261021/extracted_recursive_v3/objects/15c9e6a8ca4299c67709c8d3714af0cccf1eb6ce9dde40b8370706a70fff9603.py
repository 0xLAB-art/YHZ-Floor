import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a dict for quick ciphertext lookup
    ct_dict = {}
    for ct in ciphertexts:
        ct_dict[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        ct = ct_dict[msg_idx]
        
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            ct_byte = ct[pos]
            ks_byte = ct_byte ^ pt_byte
            keystream[pos] = ks_byte
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_dict[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Should not happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()