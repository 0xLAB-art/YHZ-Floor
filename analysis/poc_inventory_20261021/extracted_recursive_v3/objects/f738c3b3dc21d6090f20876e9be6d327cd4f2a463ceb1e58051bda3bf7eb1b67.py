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
        plaintext = bytes.fromhex(kp['data'])
        if msg_idx not in known_plaintexts:
            known_plaintexts[msg_idx] = {}
        known_plaintexts[msg_idx][offset] = plaintext
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Stream cipher reuse attack: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can find P2 = (C1 XOR C2) XOR P1
    
    # Find a known plaintext that overlaps with our target
    result_plaintext = bytearray(target_length)
    
    for known_msg_idx, offsets in known_plaintexts.items():
        if known_msg_idx == target_msg_idx:
            # Same message - direct lookup
            for offset, plaintext in offsets.items():
                if offset <= target_offset < offset + len(plaintext):
                    start_in_known = target_offset - offset
                    copy_len = min(len(plaintext) - start_in_known, target_length)
                    result_plaintext[0:copy_len] = plaintext[start_in_known:start_in_known + copy_len]
        else:
            # Different message - XOR attack
            for offset, plaintext in offsets.items():
                # Calculate overlap between known plaintext and target
                known_start = offset
                known_end = offset + len(plaintext)
                target_start = target_offset
                target_end = target_offset + target_length
                
                # Find overlapping region in absolute coordinates
                overlap_start = max(known_start, target_start)
                overlap_end = min(known_end, target_end)
                
                if overlap_start < overlap_end:
                    # We have overlap
                    overlap_length = overlap_end - overlap_start
                    
                    # Position in known plaintext
                    pos_in_known = overlap_start - known_start
                    # Position in target
                    pos_in_target = overlap_start - target_start
                    
                    # XOR the ciphertexts and known plaintext
                    for i in range(overlap_length):
                        c1 = ciphertexts[known_msg_idx][known_start + pos_in_known + i]
                        c2 = ciphertexts[target_msg_idx][target_start + pos_in_target + i]
                        p1 = plaintext[pos_in_known + i]
                        
                        # C1 = P1 XOR K, C2 = P2 XOR K
                        # C1 XOR C2 = P1 XOR P2
                        # P2 = (C1 XOR C2) XOR P1
                        p2 = c1 ^ c2 ^ p1
                        result_plaintext[pos_in_target + i] = p2
    
    result = {"plaintext": result_plaintext.hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()