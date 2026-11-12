import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertext hex strings to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build known plaintext map: (message_index, offset) -> plaintext_bytes
    known_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        for i, byte in enumerate(pt_data):
            known_map[(msg_idx, offset + i)] = byte
    
    # Extract keystream bytes from known plaintexts
    # In a stream cipher: ciphertext = plaintext XOR keystream
    # So: keystream = plaintext XOR ciphertext
    keystream = {}
    for (msg_idx, pos), pt_byte in known_map.items():
        if msg_idx in ct_bytes and pos < len(ct_bytes[msg_idx]):
            ct_byte = ct_bytes[msg_idx][pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Recover the target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_bytes:
        result = {'plaintext': '00' * target_length}
        print(json.dumps(result))
        return
    
    target_ct = ct_bytes[target_msg_idx]
    recovered_pt = []
    
    for i in range(target_length):
        pos = target_offset + i
        
        # Check if we already know this plaintext byte
        if (target_msg_idx, pos) in known_map:
            recovered_pt.append(known_map[(target_msg_idx, pos)])
        # Check if we have the keystream byte at this position
        elif pos in keystream and pos < len(target_ct):
            ct_byte = target_ct[pos]
            pt_byte = ct_byte ^ keystream[pos]
            recovered_pt.append(pt_byte)
        else:
            # Try to derive keystream from other messages
            # If multiple messages use same keystream, we can use crib-dragging
            found = False
            if pos < len(target_ct):
                # Check all other messages for known plaintext at this position
                for other_msg_idx in ct_bytes:
                    if other_msg_idx != target_msg_idx and (other_msg_idx, pos) in known_map:
                        # Derive keystream from other message
                        other_pt = known_map[(other_msg_idx, pos)]
                        other_ct = ct_bytes[other_msg_idx][pos]
                        ks_byte = other_pt ^ other_ct
                        
                        # Apply to target
                        target_ct_byte = target_ct[pos]
                        pt_byte = target_ct_byte ^ ks_byte
                        recovered_pt.append(pt_byte)
                        found = True
                        break
            
            if not found:
                recovered_pt.append(0)
    
    plaintext_hex = ''.join(f'{b:02x}' for b in recovered_pt)
    result = {'plaintext': plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
