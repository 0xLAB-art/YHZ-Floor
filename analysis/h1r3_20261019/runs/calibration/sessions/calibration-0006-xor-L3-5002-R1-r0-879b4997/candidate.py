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
    
    # Build known plaintext map
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = bytes.fromhex(kp['data'])
        if msg_idx not in known:
            known[msg_idx] = {}
        for i, b in enumerate(pt_bytes):
            known[msg_idx][offset + i] = b
    
    # Extract keystream from known plaintexts
    keystream = {}
    for msg_idx in known:
        for pos, pt_byte in known[msg_idx].items():
            ct_byte = ct_bytes[msg_idx][pos]
            ks_byte = ct_byte ^ pt_byte
            if pos in keystream:
                # Verify consistency
                if keystream[pos] != ks_byte:
                    pass  # Should not happen in a valid stream cipher reuse
            else:
                keystream[pos] = ks_byte
    
    # Recover target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            result.append(pt_byte)
        else:
            # No keystream byte available - should not happen with enough known plaintexts
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == '__main__':
    main()
