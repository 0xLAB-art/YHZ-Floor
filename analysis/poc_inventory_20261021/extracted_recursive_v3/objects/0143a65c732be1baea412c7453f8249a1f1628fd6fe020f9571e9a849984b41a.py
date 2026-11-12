import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertext for message_index 0
    ct0 = None
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            ct0 = bytes.fromhex(ct['data'])
            break
    
    # Find the ciphertext for message_index 1
    ct1 = None
    for ct in ciphertexts:
        if ct['message_index'] == 1:
            ct1 = bytes.fromhex(ct['data'])
            break
    
    # Find the known plaintext for message_index 0
    pt0 = None
    pt0_offset = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            pt0 = bytes.fromhex(kp['data'])
            pt0_offset = kp['offset']
            break
    
    # This is a stream cipher reuse attack
    # If C0 = P0 XOR K and C1 = P1 XOR K (same key K)
    # Then P1 = C1 XOR K = C1 XOR (C0 XOR P0)
    
    # Extract the keystream from message 0
    keystream = bytes(c ^ p for c, p in zip(ct0[pt0_offset:pt0_offset+len(pt0)], pt0))
    
    # Use the keystream to decrypt message 1
    start = target['offset']
    length = target['length']
    
    plaintext = bytes(ct1[start + i] ^ keystream[i] for i in range(length))
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()