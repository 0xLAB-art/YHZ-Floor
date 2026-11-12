import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a map of ciphertexts by message_index
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        if msg_idx in ct_map:
            ct = ct_map[msg_idx]
            # Recover keystream: keystream = plaintext XOR ciphertext
            for i, pt_byte in enumerate(pt_data):
                pos = offset + i
                if pos < len(ct):
                    ks_byte = pt_byte ^ ct[pos]
                    keystream[pos] = ks_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_map:
        print(json.dumps({"plaintext": "00" * target_length}))
        return
    
    target_ct = ct_map[target_msg_idx]
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            # Decrypt: plaintext = ciphertext XOR keystream
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Unknown keystream byte - shouldn't happen if problem is solvable
            plaintext.append(0)
    
    plaintext_hex = bytes(plaintext).hex()
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == '__main__':
    main()