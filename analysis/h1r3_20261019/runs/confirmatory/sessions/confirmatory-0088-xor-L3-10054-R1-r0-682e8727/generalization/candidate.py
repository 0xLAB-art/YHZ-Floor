import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_bytes[msg_idx] = bytes.fromhex(ct['data'])
    
    # Recover keystream from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        # XOR plaintext with ciphertext to get keystream
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            ct_byte = ct_bytes[msg_idx][pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt using recovered keystream
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Should not happen if we have enough known plaintexts
            # But handle gracefully
            plaintext.append(0)
    
    # Output result
    result = {
        'plaintext': bytes(plaintext).hex()
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()
