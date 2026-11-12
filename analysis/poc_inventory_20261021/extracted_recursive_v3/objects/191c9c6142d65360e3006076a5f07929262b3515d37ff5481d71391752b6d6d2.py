import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Build a mapping of message_index to ciphertext
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = base64.b64decode(ct['data'])
    
    # Build a mapping of message_index to known plaintext segments
    pt_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        if msg_idx not in pt_map:
            pt_map[msg_idx] = {}
        pt_map[msg_idx][offset] = plaintext
    
    # Extract target parameters
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # This is a stream cipher reuse attack
    # If we have plaintext P0 at offset O in message M0 and ciphertext C0,
    # and we want plaintext P1 at the same offset O in message M1 with ciphertext C1,
    # then: C0 = P0 XOR K and C1 = P1 XOR K (where K is the keystream)
    # Therefore: P1 = C1 XOR C0 XOR P0
    
    # Find a known plaintext that overlaps with our target
    result_bytes = bytearray(target_length)
    
    for known_msg_idx in pt_map:
        for known_offset, known_plaintext in pt_map[known_msg_idx].items():
            known_len = len(known_plaintext)
            known_ciphertext = ct_map[known_msg_idx][known_offset:known_offset + known_len]
            
            # Check if this known plaintext helps us recover the target
            # We need the keystream at positions [target_offset, target_offset + target_length)
            # The known plaintext gives us keystream at [known_offset, known_offset + known_len)
            
            # Calculate overlap
            overlap_start = max(target_offset, known_offset)
            overlap_end = min(target_offset + target_length, known_offset + known_len)
            
            if overlap_start < overlap_end:
                # There is overlap
                for i in range(overlap_start, overlap_end):
                    # Position i in the keystream
                    # Recover keystream byte at position i
                    known_pt_idx = i - known_offset
                    keystream_byte = known_ciphertext[known_pt_idx] ^ known_plaintext[known_pt_idx]
                    
                    # Use keystream to decrypt target
                    target_ct_idx = i - target_offset
                    target_ciphertext = ct_map[target_msg_idx]
                    result_bytes[target_ct_idx] = target_ciphertext[i] ^ keystream_byte
    
    # Convert to hex
    plaintext_hex = result_bytes.hex()
    
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == '__main__':
    main()