import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        ct_data[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build a map of known plaintext bytes
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known:
            known[msg_idx] = {}
        for i, byte in enumerate(data):
            known[msg_idx][offset + i] = byte
    
    # Recover keystream from known plaintexts
    keystream = {}
    for msg_idx in known:
        for pos, pt_byte in known[msg_idx].items():
            ct_byte = ct_data[msg_idx][pos]
            ks_byte = ct_byte ^ pt_byte
            if pos in keystream and keystream[pos] != ks_byte:
                # Consistency check - should not happen with valid data
                pass
            keystream[pos] = ks_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = ct_data[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If keystream is not known at this position, we cannot decrypt
            # This should not happen if sufficient known plaintexts are provided
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()