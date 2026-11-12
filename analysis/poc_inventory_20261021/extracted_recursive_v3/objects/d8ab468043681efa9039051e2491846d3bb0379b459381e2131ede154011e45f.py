import json
import sys
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        data = base64.b64decode(ct['data'])
        ciphertexts[idx] = data
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        idx = kp['message_index']
        offset = kp['offset']
        data = base64.b64decode(kp['data'])
        if idx not in known_plaintexts:
            known_plaintexts[idx] = {}
        known_plaintexts[idx][offset] = data
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Stream cipher key reuse attack
    # If C0 = P0 XOR K and C1 = P1 XOR K (same key K)
    # Then C0 XOR C1 = P0 XOR P1
    # If we know P0, then P1 = P0 XOR C0 XOR C1
    
    # Find a known plaintext we can use
    for known_msg_idx in known_plaintexts:
        for known_offset in known_plaintexts[known_msg_idx]:
            known_plaintext = known_plaintexts[known_msg_idx][known_offset]
            known_ciphertext = ciphertexts[known_msg_idx]
            target_ciphertext = ciphertexts[target_msg_idx]
            
            # Extract the relevant portions
            known_ct_segment = known_ciphertext[known_offset:known_offset + len(known_plaintext)]
            target_ct_segment = target_ciphertext[target_offset:target_offset + target_length]
            
            # We need the segments to overlap in terms of the keystream position
            # Assuming the same keystream is used at the same position:
            # Extract keystream from known: K = P0 XOR C0
            keystream = bytes(p ^ c for p, c in zip(known_plaintext, known_ct_segment))
            
            # Now decrypt target using the keystream: P1 = C1 XOR K
            # We need enough keystream bytes
            if len(keystream) >= target_length:
                target_plaintext = bytes(c ^ k for c, k in zip(target_ct_segment, keystream[:target_length]))
                result = {"plaintext": target_plaintext.hex()}
                print(json.dumps(result))
                return
    
    # If we reach here, something went wrong
    print(json.dumps({"plaintext": "00" * target_length}))

if __name__ == "__main__":
    main()