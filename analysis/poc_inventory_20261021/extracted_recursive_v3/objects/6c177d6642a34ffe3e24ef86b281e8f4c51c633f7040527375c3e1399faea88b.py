import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known_plaintexts:
            known_plaintexts[msg_idx] = {}
        known_plaintexts[msg_idx][offset] = data
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # This is a many-time pad attack
    # If C0 = P0 XOR K and C1 = P1 XOR K (same key K)
    # Then C0 XOR C1 = P0 XOR P1
    # If we know P0, then P1 = P0 XOR C0 XOR C1
    
    # Find a known plaintext we can use
    for known_msg_idx, offsets in known_plaintexts.items():
        if known_msg_idx == target_msg_idx:
            # We have plaintext for the target message itself
            if target_offset in offsets:
                plaintext_bytes = offsets[target_offset][:target_length]
                result = {"plaintext": plaintext_bytes.hex()}
                print(json.dumps(result))
                return
        else:
            # We have plaintext for a different message encrypted with the same key
            for offset, known_plaintext in offsets.items():
                if offset == target_offset:
                    # Same offset - we can recover the key stream at this position
                    known_ciphertext = ciphertexts[known_msg_idx][offset:offset+len(known_plaintext)]
                    target_ciphertext = ciphertexts[target_msg_idx][target_offset:target_offset+target_length]
                    
                    # Recover keystream: K = P XOR C
                    keystream = bytes(p ^ c for p, c in zip(known_plaintext, known_ciphertext))
                    
                    # Decrypt target: P_target = C_target XOR K
                    plaintext_bytes = bytes(c ^ k for c, k in zip(target_ciphertext, keystream[:target_length]))
                    
                    result = {"plaintext": plaintext_bytes.hex()}
                    print(json.dumps(result))
                    return

if __name__ == '__main__':
    main()