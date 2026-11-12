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
    
    # Convert known plaintexts to bytes
    kp_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in kp_map:
            kp_map[msg_idx] = {}
        for i, b in enumerate(data):
            kp_map[msg_idx][offset + i] = b
    
    # This is a stream cipher reuse attack
    # C = P XOR K, so K = C XOR P at known positions
    # We can recover keystream bytes where we have known plaintext
    
    keystream = {}
    for msg_idx, positions in kp_map.items():
        for pos, pt_byte in positions.items():
            ct_byte = ct_bytes[msg_idx][pos]
            ks_byte = ct_byte ^ pt_byte
            if pos in keystream and keystream[pos] != ks_byte:
                # Inconsistency - should not happen with correct data
                pass
            keystream[pos] = ks_byte
    
    # Now decrypt the target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # We don't have keystream for this position
            # Try to infer from other ciphertexts if possible
            # For now, we'll use 0 as placeholder (should not happen if problem is solvable)
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
