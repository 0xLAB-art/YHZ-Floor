import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertext and known plaintext for message_index 0
    ct0 = None
    pt0 = None
    
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            ct0 = bytes.fromhex(ct['data'])
            break
    
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            pt0 = bytes.fromhex(kp['data'])
            break
    
    # Find the ciphertext for message_index 1 (target)
    ct1 = None
    for ct in ciphertexts:
        if ct['message_index'] == 1:
            ct1 = bytes.fromhex(ct['data'])
            break
    
    # This is a two-time pad attack
    # If the same key K was used to encrypt both messages:
    # C0 = P0 XOR K
    # C1 = P1 XOR K
    # Therefore: K = C0 XOR P0
    # And: P1 = C1 XOR K = C1 XOR C0 XOR P0
    
    key = bytes(c ^ p for c, p in zip(ct0, pt0))
    
    # Decrypt message 1
    pt1 = bytes(c ^ k for c, k in zip(ct1, key))
    
    # Extract the target portion
    target_offset = target['offset']
    target_length = target['length']
    target_plaintext = pt1[target_offset:target_offset + target_length]
    
    # Output the result
    result = {
        "plaintext": target_plaintext.hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
