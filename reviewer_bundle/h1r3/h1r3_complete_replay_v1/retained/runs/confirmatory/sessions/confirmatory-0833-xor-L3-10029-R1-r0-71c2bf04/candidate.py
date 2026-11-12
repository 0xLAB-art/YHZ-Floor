import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a map of ciphertext data by message index
    ct_map = {}
    for ct in ciphertexts:
        idx = ct['message_index']
        ct_map[idx] = bytes.fromhex(ct['data'])
    
    # Recover keystream bytes using known plaintexts
    # For stream cipher: ciphertext = plaintext XOR keystream
    # So: keystream = plaintext XOR ciphertext
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        if msg_idx not in ct_map:
            continue
            
        ciphertext = ct_map[msg_idx]
        
        # Extract keystream bytes at this offset
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                ct_byte = ciphertext[pos]
                ks_byte = pt_byte ^ ct_byte
                keystream[pos] = ks_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_map:
        print(json.dumps({"plaintext": "00" * target_length}))
        return
    
    target_ct = ct_map[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            ct_byte = target_ct[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # No keystream recovered for this position
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()
