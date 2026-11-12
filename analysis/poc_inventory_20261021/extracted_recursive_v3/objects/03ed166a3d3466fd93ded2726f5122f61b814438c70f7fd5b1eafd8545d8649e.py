import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Parse known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known_plaintexts:
            known_plaintexts[msg_idx] = {}
        known_plaintexts[msg_idx][offset] = data
    
    # Parse target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Recover keystream from known plaintext
    # We know plaintext for message 0 at offset 0
    known_msg_idx = 0
    known_offset = 0
    known_plaintext = known_plaintexts[known_msg_idx][known_offset]
    
    # Extract corresponding ciphertext portion
    c0 = ciphertexts[known_msg_idx][known_offset:known_offset + len(known_plaintext)]
    
    # Recover keystream: K = C0 ⊕ P0
    keystream = bytes(c ^ p for c, p in zip(c0, known_plaintext))
    
    # Decrypt target ciphertext: P1 = C1 ⊕ K
    c1 = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
    plaintext = bytes(c ^ k for c, k in zip(c1, keystream[:target_length]))
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()