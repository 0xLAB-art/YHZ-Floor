import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex strings to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # Determine the maximum length needed
    max_len = max(len(ct) for ct in ct_bytes)
    
    # Recover keystream using known plaintexts
    # keystream[i] = ciphertext[msg_idx][offset+i] XOR plaintext[i]
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = bytes.fromhex(kp['data'])
        
        ct = ct_bytes[msg_idx]
        
        for i, pt_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ct):
                ks_byte = ct[pos] ^ pt_byte
                keystream[pos] = ks_byte
    
    # Extract target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
