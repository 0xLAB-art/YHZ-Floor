import sys
import json
import base64
from typing import List, Tuple

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append((ct['message_index'], data))
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        plaintext_bytes = base64.b64decode(kp['data'])
        known_plaintexts.append((kp['message_index'], kp['offset'], plaintext_bytes))
    
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Get ciphertexts as list indexed by message_index
    max_idx = max(ct[0] for ct in ciphertexts)
    ct_list = [None] * (max_idx + 1)
    for msg_idx, data in ciphertexts:
        ct_list[msg_idx] = data
    
    # This is a stream cipher reuse attack
    # If keystream K is reused: C1 = P1 ⊕ K, C2 = P2 ⊕ K
    # Then C1 ⊕ C2 = P1 ⊕ P2
    # If we know P1, we can find P2 = P1 ⊕ C1 ⊕ C2
    
    # Build keystream recovery from known plaintexts
    max_pos = max(kp[1] + len(kp[2]) for kp in known_plaintexts)
    max_ct_len = max(len(ct[1]) for ct in ciphertexts)
    max_pos = max(max_pos, target_offset + target_length)
    
    # Recover keystream at each position
    keystream = [None] * max_pos
    
    for msg_idx, offset, plaintext in known_plaintexts:
        ct = ct_list[msg_idx]
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ct):
                k_byte = ct[pos] ^ p_byte
                keystream[pos] = k_byte
    
    # Now decrypt target using recovered keystream
    target_ct = ct_list[target_msg_idx]
    result = []
    
    for i in range(target_length):
        pos = target_offset + i
        if keystream[pos] is not None:
            plaintext_byte = target_ct[pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # Try to recover keystream from other ciphertexts
            # Using XOR relationships
            recovered = False
            
            # Try all pairs of messages where we know plaintext at this position
            for msg_idx_a, offset_a, plain_a in known_plaintexts:
                if offset_a <= pos < offset_a + len(plain_a):
                    # We know plaintext for message msg_idx_a at position pos
                    ct_a = ct_list[msg_idx_a]
                    if pos < len(ct_a):
                        k_byte = ct_a[pos] ^ plain_a[pos - offset_a]
                        keystream[pos] = k_byte
                        plaintext_byte = target_ct[pos] ^ k_byte
                        result.append(plaintext_byte)
                        recovered = True
                        break
            
            if not recovered:
                # Use crib dragging or other techniques
                # For now, try common patterns
                result.append(0)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in result)
    
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
