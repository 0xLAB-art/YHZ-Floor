import json
import sys

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
    
    # This is a two-time pad attack
    # ct0 = pt0 XOR key
    # ct1 = pt1 XOR key
    # We know pt0, so we can recover the key at those positions
    # key = pt0 XOR ct0
    
    # Extract the key from the known plaintext
    key = bytes(p ^ c for p, c in zip(pt0, ct0[pt0_offset:pt0_offset + len(pt0)]))
    
    # Now decrypt the target portion of message 1
    target_offset = target['offset']
    target_length = target['length']
    
    # Decrypt: pt1 = ct1 XOR key
    pt1_bytes = bytes(ct1[i] ^ key[i - target_offset] 
                      for i in range(target_offset, target_offset + target_length))
    
    result = {
        "plaintext": pt1_bytes.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
