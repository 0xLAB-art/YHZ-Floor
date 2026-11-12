import json
import sys

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
    
    # This is a two-time pad attack
    # ct0 = pt0 XOR key
    # ct1 = pt1 XOR key
    # We know pt0, so we can recover the key: key = pt0 XOR ct0
    # Then we can decrypt pt1: pt1 = ct1 XOR key
    
    # Extract the key from the known plaintext
    key = bytes(a ^ b for a, b in zip(pt0, ct0[pt0_offset:pt0_offset+len(pt0)]))
    
    # Decrypt the target message
    target_offset = target['offset']
    target_length = target['length']
    target_ct = ct1[target_offset:target_offset+target_length]
    target_key = key[target_offset:target_offset+target_length]
    
    plaintext = bytes(a ^ b for a, b in zip(target_ct, target_key))
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
