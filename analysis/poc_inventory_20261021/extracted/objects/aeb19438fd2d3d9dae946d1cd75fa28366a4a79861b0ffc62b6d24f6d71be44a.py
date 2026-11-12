import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = [bytes.fromhex(ct['data']) for ct in ciphertexts]
    
    # Extract known plaintext information
    kp = known_plaintexts[0]
    kp_data = bytes.fromhex(kp['data'])
    kp_msg_idx = kp['message_index']
    kp_offset = kp['offset']
    
    # Recover keystream at known plaintext position
    # plaintext XOR ciphertext = keystream
    keystream_fragment = bytes(p ^ c for p, c in zip(kp_data, ct_bytes[kp_msg_idx][kp_offset:kp_offset+len(kp_data)]))
    
    # Target information
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Check if we have keystream overlap with target
    kp_start = kp_offset
    kp_end = kp_offset + len(keystream_fragment)
    target_start = target_offset
    target_end = target_offset + target_length
    
    # Calculate overlap
    overlap_start = max(kp_start, target_start)
    overlap_end = min(kp_end, target_end)
    
    if overlap_start >= overlap_end:
        # No overlap - we cannot recover the target
        print(json.dumps({
            "status": "UNDERDETERMINED",
            "reason": "known plaintext does not overlap with target position"
        }))
        return
    
    # We have some overlap, but check if it covers the entire target
    if overlap_start > target_start or overlap_end < target_end:
        # Partial overlap - insufficient information
        coverage = overlap_end - overlap_start
        needed = target_length
        print(json.dumps({
            "status": "UNDERDETERMINED",
            "reason": f"only {coverage} of {needed} target bytes covered by known keystream"
        }))
        return
    
    # Full coverage - we can recover the target
    # Extract the relevant keystream portion for the target
    ks_offset_in_fragment = target_start - kp_start
    target_keystream = keystream_fragment[ks_offset_in_fragment:ks_offset_in_fragment+target_length]
    
    # Decrypt target ciphertext
    target_ciphertext = ct_bytes[target_msg_idx][target_start:target_end]
    target_plaintext = bytes(c ^ k for c, k in zip(target_ciphertext, target_keystream))
    
    print(json.dumps({
        "status": "UNDERDETERMINED",
        "reason": "insufficient keystream coverage for target"
    }))

if __name__ == '__main__':
    main()
