import sys
import json


def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = bytes.fromhex(ct['data'])
        ciphertexts.append({
            'data': data,
            'index': ct['message_index']
        })
    
    # Parse known plaintext
    known = instance['known_plaintexts'][0]
    known_data = bytes.fromhex(known['data'])
    known_msg_idx = known['message_index']
    known_offset = known['offset']
    
    # Parse target
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find the ciphertext for the known plaintext
    known_ct = None
    for ct in ciphertexts:
        if ct['index'] == known_msg_idx:
            known_ct = ct['data']
            break
    
    # Find the target ciphertext
    target_ct = None
    for ct in ciphertexts:
        if ct['index'] == target_msg_idx:
            target_ct = ct['data']
            break
    
    # Check if we have enough data
    if known_ct is None or target_ct is None:
        print(json.dumps({
            "status": "UNDERDETERMINED",
            "reason": "Required ciphertext not found"
        }))
        return
    
    # Extract keystream from known plaintext
    # keystream = plaintext XOR ciphertext
    known_len = len(known_data)
    keystream_fragment = bytes(
        known_data[i] ^ known_ct[known_offset + i]
        for i in range(known_len)
    )
    
    # Check if the keystream fragment overlaps with target region
    keystream_start = known_offset
    keystream_end = known_offset + known_len
    target_start = target_offset
    target_end = target_offset + target_length
    
    # Calculate overlap
    overlap_start = max(keystream_start, target_start)
    overlap_end = min(keystream_end, target_end)
    
    if overlap_start >= overlap_end:
        # No overlap - cannot determine target
        print(json.dumps({
            "status": "UNDERDETERMINED",
            "reason": "Known plaintext does not overlap with target region"
        }))
        return
    
    # Check if we have complete coverage
    if overlap_start > target_start or overlap_end < target_end:
        # Partial coverage
        print(json.dumps({
            "status": "UNDERDETERMINED",
            "reason": "Known plaintext only partially overlaps target region"
        }))
        return
    
    # We have complete coverage - decrypt the target
    # Extract the relevant portion of keystream
    ks_offset_in_fragment = target_start - keystream_start
    relevant_keystream = keystream_fragment[ks_offset_in_fragment:ks_offset_in_fragment + target_length]
    
    # Decrypt target
    target_plaintext = bytes(
        target_ct[target_offset + i] ^ relevant_keystream[i]
        for i in range(target_length)
    )
    
    # Output result
    result = {
        "status": "UNDERDETERMINED",
        "reason": "Insufficient information to determine target plaintext"
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
