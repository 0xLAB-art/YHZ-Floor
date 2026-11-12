import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Find the known plaintext for message 0
    known_pt = None
    known_ct = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            known_pt = bytes.fromhex(kp['data'])
            known_offset = kp['offset']
            break
    
    # Find ciphertext for message 0
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            known_ct = bytes.fromhex(ct['data'])
            break
    
    # Find target ciphertext
    target_ct = None
    for ct in ciphertexts:
        if ct['message_index'] == target['message_index']:
            target_ct = bytes.fromhex(ct['data'])
            break
    
    # Extract keystream from known plaintext/ciphertext pair
    # In stream cipher: ciphertext = plaintext XOR keystream
    # So: keystream = plaintext XOR ciphertext
    keystream = bytes(p ^ c for p, c in zip(known_pt, known_ct[known_offset:known_offset+len(known_pt)]))
    
    # Decrypt target using the same keystream
    # plaintext = ciphertext XOR keystream
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = bytes(c ^ k for c, k in zip(
        target_ct[target_offset:target_offset+target_length],
        keystream[:target_length]
    ))
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
