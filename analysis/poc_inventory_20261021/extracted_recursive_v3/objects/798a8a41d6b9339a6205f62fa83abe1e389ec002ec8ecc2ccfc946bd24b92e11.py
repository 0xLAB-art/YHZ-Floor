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
    # C0 = P0 XOR K
    # C1 = P1 XOR K
    # Where K is the keystream
    
    # From known P0 and C0, we can recover the keystream:
    # K = P0 XOR C0
    
    # Extract the relevant portion of the keystream
    keystream = bytes(p ^ c for p, c in zip(pt0, ct0[pt0_offset:pt0_offset + len(pt0)]))
    
    # Now decrypt the target from message_index 1
    # P1 = C1 XOR K
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

if __name__ == '__main__':
    main()