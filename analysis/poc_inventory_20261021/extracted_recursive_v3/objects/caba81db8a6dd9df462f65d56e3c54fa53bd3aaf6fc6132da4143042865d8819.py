import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = base64.b64decode(ct['data'])
    
    # Parse known plaintexts
    known = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = base64.b64decode(kp['data'])
        if msg_idx not in known:
            known[msg_idx] = {}
        known[msg_idx][offset] = data
    
    # Get target info
    target_msg = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Extract keystream from known plaintext
    # Assumption: stream cipher reuse, so keystream is same across messages
    known_msg = 0
    known_offset = 0
    known_plaintext = known[known_msg][known_offset]
    known_ciphertext = ciphertexts[known_msg][known_offset:known_offset + len(known_plaintext)]
    
    # Recover keystream: keystream = plaintext XOR ciphertext
    keystream = bytes(p ^ c for p, c in zip(known_plaintext, known_ciphertext))
    
    # Decrypt target using the keystream
    target_ciphertext = ciphertexts[target_msg][target_offset:target_offset + target_length]
    target_plaintext = bytes(c ^ k for c, k in zip(target_ciphertext, keystream[:target_length]))
    
    # Output result
    result = {
        "plaintext": target_plaintext.hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()