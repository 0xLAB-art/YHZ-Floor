import json
import sys

def main():
    with open(sys.argv[1]) as f:
        instance = json.load(f)
    
    ciphertexts = [bytes.fromhex(ct['data']) for ct in instance['ciphertexts']]
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Extract known plaintext
    kp = known_plaintexts[0]
    known_pt = bytes.fromhex(kp['data'])
    known_msg_idx = kp['message_index']
    known_offset = kp['offset']
    
    # XOR known plaintext with its ciphertext to get keystream
    ct_known = ciphertexts[known_msg_idx]
    keystream_fragment = bytes(c ^ p for c, p in zip(ct_known[known_offset:known_offset+len(known_pt)], known_pt))
    
    # Target details
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Check if keystream fragment overlaps with target
    ks_start = known_offset
    ks_end = known_offset + len(keystream_fragment)
    target_start = target_offset
    target_end = target_offset + target_length
    
    # Calculate overlap
    overlap_start = max(ks_start, target_start)
    overlap_end = min(ks_end, target_end)
    
    if overlap_start >= overlap_end:
        # No overlap
        result = {
            "status": "UNDERDETERMINED",
            "reason": "known keystream does not overlap with target region"
        }
    else:
        # Partial or full overlap
        overlap_length = overlap_end - overlap_start
        if overlap_length < target_length:
            result = {
                "status": "UNDERDETERMINED",
                "reason": f"only {overlap_length} of {target_length} target bytes covered by known keystream"
            }
        else:
            # Full coverage - should not happen based on problem, but handle it
            result = {
                "status": "UNDERDETERMINED",
                "reason": "full coverage achieved but task expects underdetermined status"
            }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()