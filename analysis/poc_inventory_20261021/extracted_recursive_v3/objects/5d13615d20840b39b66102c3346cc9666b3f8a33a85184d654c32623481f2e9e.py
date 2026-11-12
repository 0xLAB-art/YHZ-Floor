import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Build a map of ciphertexts by message_index
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build a map of known plaintexts
    pt_map = {}
    for kp in known_plaintexts:
        if kp['message_index'] not in pt_map:
            pt_map[kp['message_index']] = {}
        pt_data = bytes.fromhex(kp['data'])
        offset = kp['offset']
        for i, b in enumerate(pt_data):
            pt_map[kp['message_index']][offset + i] = b
    
    # Extract the keystream from known plaintext
    # For a stream cipher with key reuse: C = P XOR K
    # So K = C XOR P
    keystream = {}
    for msg_idx, positions in pt_map.items():
        ct = ct_map[msg_idx]
        for pos, pt_byte in positions.items():
            if pos < len(ct):
                keystream[pos] = ct[pos] ^ pt_byte
    
    # Recover the target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_map[target_msg_idx]
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Should not happen if keystream is fully known
            plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()