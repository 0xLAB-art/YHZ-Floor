import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_bytes[msg_idx] = bytes.fromhex(ct['data'])
    
    # Build known plaintext mapping: position -> {message_index: plaintext_byte}
    known_at_pos = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        for i, byte in enumerate(data):
            pos = offset + i
            if pos not in known_at_pos:
                known_at_pos[pos] = {}
            known_at_pos[pos][msg_idx] = byte
    
    # Recover keystream
    # For stream cipher: C = P XOR K, so K = P XOR C
    keystream = {}
    for pos, msg_dict in known_at_pos.items():
        for msg_idx, pt_byte in msg_dict.items():
            if msg_idx in ct_bytes and pos < len(ct_bytes[msg_idx]):
                ct_byte = ct_bytes[msg_idx][pos]
                keystream[pos] = pt_byte ^ ct_byte
                break
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_bytes:
        print(json.dumps({"plaintext": "00" * target_length}))
        return
    
    target_ct = ct_bytes[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream at this position, we need to infer it
            # This shouldn't happen if the instance is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == '__main__':
    main()
