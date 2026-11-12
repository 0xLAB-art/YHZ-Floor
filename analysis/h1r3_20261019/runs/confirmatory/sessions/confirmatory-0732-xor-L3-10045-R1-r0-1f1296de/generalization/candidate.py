import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build known plaintext dictionary
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known:
            known[msg_idx] = {}
        for i, byte in enumerate(data):
            known[msg_idx][offset + i] = byte
    
    # For stream cipher reuse attack:
    # C_i = P_i XOR K
    # C_j = P_j XOR K
    # Therefore: C_i XOR C_j = P_i XOR P_j
    # If we know P_j, then: P_i = C_i XOR C_j XOR P_j
    
    target_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Recover target plaintext
    plaintext = bytearray(target_length)
    recovered = [False] * target_length
    
    # Try to recover each byte of the target
    for pos in range(target_length):
        absolute_pos = target_offset + pos
        
        # Look for known plaintext at this position in other messages
        for msg_idx in known:
            if msg_idx == target_idx:
                continue
            if absolute_pos in known[msg_idx]:
                # We have P_j at this position
                # P_target = C_target XOR C_j XOR P_j
                if absolute_pos < len(ct_bytes[target_idx]) and absolute_pos < len(ct_bytes[msg_idx]):
                    c_target = ct_bytes[target_idx][absolute_pos]
                    c_other = ct_bytes[msg_idx][absolute_pos]
                    p_other = known[msg_idx][absolute_pos]
                    p_target = c_target ^ c_other ^ p_other
                    plaintext[pos] = p_target
                    recovered[pos] = True
                    break
    
    # If we have known plaintext in the target itself, use it directly
    if target_idx in known:
        for abs_pos in known[target_idx]:
            rel_pos = abs_pos - target_offset
            if 0 <= rel_pos < target_length:
                plaintext[rel_pos] = known[target_idx][abs_pos]
                recovered[rel_pos] = True
    
    # For any remaining unrecovered bytes, try a different approach
    # We can also use: if we know P_i and P_j, we can derive K at that position
    # K = P_i XOR C_i, then use K to decrypt other messages
    
    keystream = {}
    for msg_idx in known:
        for abs_pos in known[msg_idx]:
            if abs_pos < len(ct_bytes[msg_idx]):
                k_byte = known[msg_idx][abs_pos] ^ ct_bytes[msg_idx][abs_pos]
                if abs_pos not in keystream:
                    keystream[abs_pos] = k_byte
    
    # Use recovered keystream to decrypt target
    for pos in range(target_length):
        if not recovered[pos]:
            absolute_pos = target_offset + pos
            if absolute_pos in keystream and absolute_pos < len(ct_bytes[target_idx]):
                plaintext[pos] = ct_bytes[target_idx][absolute_pos] ^ keystream[absolute_pos]
                recovered[pos] = True
    
    result = {
        "plaintext": plaintext.hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
