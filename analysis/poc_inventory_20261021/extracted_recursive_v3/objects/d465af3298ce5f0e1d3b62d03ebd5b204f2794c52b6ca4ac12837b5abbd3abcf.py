import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        ct_data[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Parse known plaintexts
    kp_data = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in kp_data:
            kp_data[msg_idx] = {}
        for i, byte in enumerate(data):
            kp_data[msg_idx][offset + i] = byte
    
    # Extract keystream from known plaintexts
    # For stream cipher: C = P XOR K, so K = P XOR C
    keystream = {}
    for msg_idx, positions in kp_data.items():
        for pos, plaintext_byte in positions.items():
            ciphertext_byte = ct_data[msg_idx][pos]
            keystream[pos] = plaintext_byte ^ ciphertext_byte
    
    # Recover target plaintext using the keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_offset, target_offset + target_length):
        if i in keystream:
            # We have the keystream at this position
            ct_byte = ct_data[target_msg_idx][i]
            pt_byte = ct_byte ^ keystream[i]
            plaintext_bytes.append(pt_byte)
        else:
            # We need to recover the keystream from other messages
            # Try to find another message with known plaintext at this position
            found = False
            for msg_idx in ct_data:
                if msg_idx in kp_data and i in kp_data[msg_idx]:
                    ct_byte = ct_data[msg_idx][i]
                    pt_byte = kp_data[msg_idx][i]
                    keystream[i] = ct_byte ^ pt_byte
                    
                    # Now decrypt target
                    target_ct_byte = ct_data[target_msg_idx][i]
                    target_pt_byte = target_ct_byte ^ keystream[i]
                    plaintext_bytes.append(target_pt_byte)
                    found = True
                    break
            
            if not found:
                # Use crib-dragging or statistical analysis
                # Try common patterns
                plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()