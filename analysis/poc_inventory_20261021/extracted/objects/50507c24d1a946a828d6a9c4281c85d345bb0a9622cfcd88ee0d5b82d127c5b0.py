import json
import sys

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
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    target_ct = ct_bytes[target_msg_idx]
    
    # Recover keystream from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = bytes.fromhex(kp['data'])
        ct = ct_bytes[msg_idx]
        
        for i, pt_byte in enumerate(pt_bytes):
            pos = offset + i
            ct_byte = ct[pos]
            key_byte = pt_byte ^ ct_byte
            keystream[pos] = key_byte
    
    # Decrypt target using recovered keystream
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # No keystream available - this shouldn't happen if puzzle is solvable
            plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()
