import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts from hex to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build a map of known plaintext bytes
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        for i, b in enumerate(data):
            pos = offset + i
            if pos not in known:
                known[pos] = {}
            known[pos][msg_idx] = b
    
    # For stream cipher reuse attack:
    # C_i = P_i XOR K
    # C_j = P_j XOR K
    # Therefore: C_i XOR C_j = P_i XOR P_j
    # If we know P_j, then: P_i = C_i XOR C_j XOR P_j
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = bytearray(target_length)
    
    for pos in range(target_offset, target_offset + target_length):
        pt_byte = None
        
        # Check if we already know this position for the target message
        if pos in known and target_msg_idx in known[pos]:
            pt_byte = known[pos][target_msg_idx]
        else:
            # Try to recover from known plaintexts in other messages
            for other_msg_idx in known.get(pos, {}):
                if other_msg_idx != target_msg_idx:
                    # We know P_j at position pos for message other_msg_idx
                    # P_target = C_target XOR C_other XOR P_other
                    c_target = ct_bytes[target_msg_idx][pos]
                    c_other = ct_bytes[other_msg_idx][pos]
                    p_other = known[pos][other_msg_idx]
                    pt_byte = c_target ^ c_other ^ p_other
                    break
        
        if pt_byte is not None:
            plaintext[pos - target_offset] = pt_byte
    
    result = {
        "plaintext": plaintext.hex()
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()