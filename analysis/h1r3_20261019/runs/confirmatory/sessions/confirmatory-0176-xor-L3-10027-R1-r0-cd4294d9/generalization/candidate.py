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
    ciphertext_map = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        data = bytes.fromhex(ct['data'])
        ciphertext_map[msg_idx] = data
    
    # Recover keystream from known plaintexts
    # keystream[position] = ciphertext[message_index][position] XOR plaintext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        if msg_idx in ciphertext_map:
            ciphertext = ciphertext_map[msg_idx]
            
            for i, pt_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    ct_byte = ciphertext[pos]
                    ks_byte = ct_byte ^ pt_byte
                    keystream[pos] = ks_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ciphertext_map:
        print(json.dumps({"plaintext": "00" * target_length}))
        return
    
    target_ciphertext = ciphertext_map[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream for this position, output 0x00
            plaintext_bytes.append(0x00)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()
