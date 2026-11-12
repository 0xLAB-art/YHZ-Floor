import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the data
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Get the known plaintext for message 0
    known_pt = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0 and kp['offset'] == 0:
            known_pt = bytes.fromhex(kp['data'])
            break
    
    # Get ciphertext 0 and ciphertext 1
    ct0 = ciphertexts[0]
    ct1 = ciphertexts[1]
    
    # Recover the keystream: K = C0 XOR P0
    keystream = bytes(c ^ p for c, p in zip(ct0, known_pt))
    
    # Decrypt message 1: P1 = C1 XOR K
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext1 = bytes(c ^ k for c, k in zip(ct1, keystream))
    
    # Extract the target portion
    target_plaintext = plaintext1[target_offset:target_offset + target_length]
    
    # Output as hex
    result = {
        "plaintext": target_plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()