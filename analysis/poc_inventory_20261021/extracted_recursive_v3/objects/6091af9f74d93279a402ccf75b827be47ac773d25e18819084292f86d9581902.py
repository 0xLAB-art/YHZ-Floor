import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) for ct in instance['ciphertexts']}
    known_plaintexts = {kp['message_index']: {'data': bytes.fromhex(kp['data']), 'offset': kp['offset']} for kp in instance['known_plaintexts']}
    target = instance['target']
    
    # Extract known plaintext for message 0
    known_msg_idx = 0
    known_plaintext = known_plaintexts[known_msg_idx]['data']
    known_offset = known_plaintexts[known_msg_idx]['offset']
    
    # Extract ciphertext for message 0
    ct0 = ciphertexts[known_msg_idx]
    
    # Recover the keystream used for message 0 at the known offset
    # In a stream cipher: C = P XOR K, so K = P XOR C
    keystream_segment = bytes(p ^ c for p, c in zip(known_plaintext, ct0[known_offset:known_offset + len(known_plaintext)]))
    
    # Extract target ciphertext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    ct_target = ciphertexts[target_msg_idx]
    
    # If the same keystream is reused (two-time pad), we can decrypt the target
    # P1 = C1 XOR K
    plaintext = bytes(c ^ k for c, k in zip(ct_target[target_offset:target_offset + target_length], keystream_segment[:target_length]))
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()