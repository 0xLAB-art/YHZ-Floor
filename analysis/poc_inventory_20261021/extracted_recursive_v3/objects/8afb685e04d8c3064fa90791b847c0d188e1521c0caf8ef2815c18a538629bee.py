import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertext for message_index 0 and 1
    ct0 = None
    ct1 = None
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            ct0 = bytes.fromhex(ct['data'])
        elif ct['message_index'] == 1:
            ct1 = bytes.fromhex(ct['data'])
    
    # Find the known plaintext for message_index 0
    pt0 = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            pt0 = bytes.fromhex(kp['data'])
            pt0_offset = kp['offset']
    
    # This is a stream cipher reuse attack
    # ct0 = pt0 XOR keystream
    # ct1 = pt1 XOR keystream
    # Therefore: keystream = pt0 XOR ct0
    # And: pt1 = ct1 XOR keystream
    
    # Extract the keystream from known plaintext
    keystream = bytes(a ^ b for a, b in zip(pt0, ct0[pt0_offset:pt0_offset + len(pt0)]))
    
    # Decrypt the target portion of message 1
    target_offset = target['offset']
    target_length = target['length']
    
    # XOR ct1 with keystream to get pt1
    pt1_segment = bytes(
        ct1[target_offset + i] ^ keystream[i] 
        for i in range(target_length)
    )
    
    result = {
        "plaintext": pt1_segment.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()