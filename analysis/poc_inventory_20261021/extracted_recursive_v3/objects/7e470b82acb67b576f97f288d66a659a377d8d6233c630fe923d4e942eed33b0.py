import json
import sys

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
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            ct_byte = ct_bytes[msg_idx][pos]
            ks_byte = ct_byte ^ pt_byte
            keystream[pos] = ks_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Should not happen if keystream is fully recovered
            plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()