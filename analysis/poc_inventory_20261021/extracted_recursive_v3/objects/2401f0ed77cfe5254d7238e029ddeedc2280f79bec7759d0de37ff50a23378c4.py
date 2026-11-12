import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the input
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        known_plaintexts[kp['message_index']] = {
            'data': bytes.fromhex(kp['data']),
            'offset': kp['offset']
        }
    
    target = instance['target']
    target_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find a known plaintext we can use
    # We need message 0's plaintext to decrypt message 1
    known_index = 0
    known_data = known_plaintexts[known_index]['data']
    known_offset = known_plaintexts[known_index]['offset']
    
    # Extract the keystream from the known plaintext
    # key = plaintext XOR ciphertext
    ct0 = ciphertexts[known_index]
    keystream = bytes(p ^ c for p, c in zip(known_data, ct0[known_offset:known_offset + len(known_data)]))
    
    # Now decrypt the target message using the recovered keystream
    # plaintext = ciphertext XOR key
    ct_target = ciphertexts[target_index]
    plaintext = bytes(c ^ k for c, k in zip(
        ct_target[target_offset:target_offset + target_length],
        keystream[0:target_length]
    ))
    
    # Output result
    result = {
        "plaintext": plaintext.hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()