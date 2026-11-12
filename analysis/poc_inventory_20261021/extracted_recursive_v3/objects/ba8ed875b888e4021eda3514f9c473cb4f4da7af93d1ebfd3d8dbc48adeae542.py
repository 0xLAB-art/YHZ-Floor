import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_bytes[msg_idx] = bytes.fromhex(ct['data'])
    
    # Build known plaintext bytes for each message
    known_pt = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        if msg_idx not in known_pt:
            known_pt[msg_idx] = {}
        
        for i, byte in enumerate(pt_data):
            known_pt[msg_idx][offset + i] = byte
    
    # This is a many-time pad attack
    # For stream cipher reuse: C_i = P_i XOR K
    # If we know P_i at position j, we can recover K[j] = C_i[j] XOR P_i[j]
    # Then we can decrypt any other message at position j: P_t[j] = C_t[j] XOR K[j]
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Recover keystream bytes
    keystream = {}
    for msg_idx, positions in known_pt.items():
        for pos, pt_byte in positions.items():
            if pos < len(ct_bytes[msg_idx]):
                key_byte = ct_bytes[msg_idx][pos] ^ pt_byte
                keystream[pos] = key_byte
    
    # Decrypt target
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(ct_bytes[target_msg_idx]):
            pt_byte = ct_bytes[target_msg_idx][pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Should not happen if instance is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
