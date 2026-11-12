import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        pt_bytes = bytes.fromhex(kp['data'])
        msg_idx = kp['message_index']
        offset = kp['offset']
        
        for i, pt_byte in enumerate(pt_bytes):
            pos = offset + i
            ct_byte = ct_bytes[msg_idx][pos]
            ks_byte = ct_byte ^ pt_byte
            
            if pos in keystream:
                assert keystream[pos] == ks_byte
            else:
                keystream[pos] = ks_byte
    
    # Recover target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            result.append(pt_byte)
        else:
            # No keystream byte available, cannot decrypt
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == '__main__':
    main()
