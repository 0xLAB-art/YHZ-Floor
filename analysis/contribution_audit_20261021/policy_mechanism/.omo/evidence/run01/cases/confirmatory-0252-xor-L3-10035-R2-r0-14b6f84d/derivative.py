import sys
import json
import base64


def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': base64.b64decode(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Build a map from message_index to ciphertext
    ct_map = {ct['message_index']: ct['data'] for ct in ciphertexts}
    
    # Decode known plaintexts
    known_pts = []
    for kp in instance['known_plaintexts']:
        known_pts.append({
            'data': base64.b64decode(kp['data']),
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    # Extract target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Build keystream recovery map: position -> keystream byte
    keystream = {}
    
    # For each known plaintext, recover keystream bytes
    for kp in known_pts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = kp['data']
        ct_data = ct_map[msg_idx]
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            ct_byte = ct_data[pos]
            ks_byte = pt_byte ^ ct_byte
            keystream[pos] = ks_byte
    
    # Now decrypt the target using recovered keystream
    target_ct = ct_map[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We have the keystream byte, so decrypt
            ct_byte = target_ct[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # We don't have this keystream byte - this shouldn't happen
            # if the challenge is solvable, but handle gracefully
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
