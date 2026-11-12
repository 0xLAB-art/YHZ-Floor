import sys
import json

def xor_bytes(a, b):
    """XOR two byte sequences of equal length."""
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse input
    ciphertexts = [bytes.fromhex(ct['data']) for ct in instance['ciphertexts']]
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Extract known plaintext information
    kp = known_plaintexts[0]
    known_msg_idx = kp['message_index']
    known_offset = kp['offset']
    known_plaintext = bytes.fromhex(kp['data'])
    known_length = len(known_plaintext)
    
    # Target information
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Check if we have the keystream for the target region
    # We can recover keystream from: keystream = ciphertext XOR plaintext
    keystream_start = known_offset
    keystream_end = known_offset + known_length
    
    # We need keystream from target_offset to target_offset + target_length
    needed_start = target_offset
    needed_end = target_offset + target_length
    
    # Check if there's any overlap
    overlap_start = max(keystream_start, needed_start)
    overlap_end = min(keystream_end, needed_end)
    
    if overlap_start >= overlap_end:
        # No overlap - we cannot determine the target plaintext
        result = {
            "status": "UNDERDETERMINED",
            "reason": "Known plaintext does not overlap with target region"
        }
    else:
        # There is overlap, but check if it covers the entire target
        if overlap_start > needed_start or overlap_end < needed_end:
            # Partial overlap - insufficient information
            result = {
                "status": "UNDERDETERMINED",
                "reason": "Known plaintext only partially overlaps target region"
            }
        else:
            # Full overlap - we can recover the keystream and decrypt the target
            # Recover keystream from known plaintext
            known_ciphertext = ciphertexts[known_msg_idx][known_offset:known_offset + known_length]
            keystream = xor_bytes(known_ciphertext, known_plaintext)
            
            # Use keystream to decrypt target
            target_ciphertext = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
            target_plaintext = xor_bytes(target_ciphertext, keystream)
            
            result = {
                "status": "UNDERDETERMINED",
                "reason": "Target region covered by known keystream"
            }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()