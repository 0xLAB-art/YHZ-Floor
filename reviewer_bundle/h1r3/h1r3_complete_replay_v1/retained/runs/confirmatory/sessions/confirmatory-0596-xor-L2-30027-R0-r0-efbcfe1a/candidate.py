import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_data[msg_idx] = bytes.fromhex(ct['data'])
    
    # Build known plaintext map: (message_index, offset) -> plaintext_bytes
    known_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = bytes.fromhex(kp['data'])
        for i, b in enumerate(pt_bytes):
            known_map[(msg_idx, offset + i)] = b
    
    # XOR stream cipher: C = P XOR K
    # If we know P and C, we can recover K at that position: K = P XOR C
    # Then use K to decrypt other ciphertexts at the same position
    
    # Recover keystream bytes
    keystream = {}
    for (msg_idx, offset), pt_byte in known_map.items():
        ct_byte = ct_data[msg_idx][offset]
        key_byte = pt_byte ^ ct_byte
        
        # Check consistency if we already have this keystream byte
        if offset in keystream:
            assert keystream[offset] == key_byte, f"Inconsistent keystream at offset {offset}"
        else:
            keystream[offset] = key_byte
    
    # Decrypt target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = ct_data[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # No keystream byte available - this shouldn't happen with proper instances
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
