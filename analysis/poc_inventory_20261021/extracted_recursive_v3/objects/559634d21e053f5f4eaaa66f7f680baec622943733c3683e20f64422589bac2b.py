import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) for ct in instance['ciphertexts']}
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Get the known plaintext for message 0
    known_pt = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            known_pt = bytes.fromhex(kp['data'])
            known_offset = kp['offset']
            break
    
    # Get ciphertexts
    ct0 = ciphertexts[0]
    ct1 = ciphertexts[1]
    
    # XOR the known plaintext with ciphertext 0 to recover the keystream
    keystream = bytes(p ^ c for p, c in zip(known_pt, ct0[known_offset:known_offset + len(known_pt)]))
    
    # XOR the keystream with ciphertext 1 to recover plaintext 1
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext1 = bytes(k ^ c for k, c in zip(keystream[target_offset:target_offset + target_length], 
                                               ct1[target_offset:target_offset + target_length]))
    
    result = {
        "plaintext": plaintext1.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()