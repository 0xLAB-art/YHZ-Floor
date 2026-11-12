import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        msg_idx = ct['message_index']
        data = base64.b64decode(ct['data'])
        ciphertexts[msg_idx] = data
    
    # Decode known plaintexts and organize by position
    known_by_position = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        for i, byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos not in known_by_position:
                known_by_position[pos] = {}
            known_by_position[pos][msg_idx] = byte
    
    # Target information
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Recover target plaintext
    result = []
    for i in range(target_length):
        pos = target_offset + i
        
        # Find any known plaintext at this position
        if pos in known_by_position:
            for known_msg_idx, known_byte in known_by_position[pos].items():
                if known_msg_idx != target_msg_idx:
                    # XOR to recover: P_target = C_target ⊕ C_known ⊕ P_known
                    c_target = ciphertexts[target_msg_idx][pos]
                    c_known = ciphertexts[known_msg_idx][pos]
                    p_target = c_target ^ c_known ^ known_byte
                    result.append(p_target)
                    break
        else:
            # No known plaintext at this position - this shouldn't happen
            # in a solvable instance, but handle gracefully
            result.append(0)
    
    # Convert to hex string
    plaintext_hex = ''.join(f'{b:02x}' for b in result)
    
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == '__main__':
    main()