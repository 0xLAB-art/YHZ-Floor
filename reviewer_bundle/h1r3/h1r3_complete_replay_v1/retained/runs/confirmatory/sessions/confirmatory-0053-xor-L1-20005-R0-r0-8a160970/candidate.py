import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Build a map of ciphertexts by message_index
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build a map of known plaintexts by message_index
    pt_map = {}
    for kp in known_plaintexts:
        if kp['message_index'] not in pt_map:
            pt_map[kp['message_index']] = {}
        pt_map[kp['message_index']][kp['offset']] = bytes.fromhex(kp['data'])
    
    # Extract what we know
    known_msg_idx = known_plaintexts[0]['message_index']
    known_offset = known_plaintexts[0]['offset']
    known_pt = bytes.fromhex(known_plaintexts[0]['data'])
    known_ct = ct_map[known_msg_idx]
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    target_ct = ct_map[target_msg_idx]
    
    # For stream cipher reuse: C1 = P1 XOR K, C2 = P2 XOR K
    # We know P1 and C1, so K = P1 XOR C1
    # Then P2 = C2 XOR K
    
    # Extract the keystream from the known plaintext/ciphertext pair
    keystream = bytes(p ^ c for p, c in zip(known_pt, known_ct[known_offset:known_offset+len(known_pt)]))
    
    # Decrypt the target using the recovered keystream
    target_pt = bytes(c ^ k for c, k in zip(target_ct[target_offset:target_offset+target_length], keystream[:target_length]))
    
    result = {
        "plaintext": target_pt.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
