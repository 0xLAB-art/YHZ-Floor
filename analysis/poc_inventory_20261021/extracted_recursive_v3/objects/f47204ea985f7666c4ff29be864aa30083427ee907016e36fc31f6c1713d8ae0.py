import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the known plaintext for message 0
    known_pt = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            known_pt = bytes.fromhex(kp['data'])
            known_offset = kp['offset']
            break
    
    # Find ciphertext for message 0
    ct0 = None
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            ct0 = bytes.fromhex(ct['data'])
            break
    
    # Find ciphertext for message 1 (target)
    ct1 = None
    for ct in ciphertexts:
        if ct['message_index'] == 1:
            ct1 = bytes.fromhex(ct['data'])
            break
    
    # XOR attack on stream cipher reuse
    # ct0 = pt0 XOR keystream
    # ct1 = pt1 XOR keystream
    # keystream = ct0 XOR pt0
    # pt1 = ct1 XOR keystream = ct1 XOR ct0 XOR pt0
    
    keystream = bytes(a ^ b for a, b in zip(ct0[known_offset:known_offset + len(known_pt)], known_pt))
    
    # Recover target plaintext
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = bytes(
        ct1[target_offset + i] ^ keystream[i]
        for i in range(target_length)
    )
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()