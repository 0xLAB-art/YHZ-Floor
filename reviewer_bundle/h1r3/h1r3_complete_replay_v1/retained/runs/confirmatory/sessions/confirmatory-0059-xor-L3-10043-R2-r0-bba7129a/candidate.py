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
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Build keystream from known plaintexts
    # keystream[position] = byte value
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        # Recover keystream at these positions
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertexts[msg_idx][pos]
            ks_byte = pt_byte ^ ct_byte
            keystream[pos] = ks_byte
    
    # Now decrypt the target
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We know the keystream at this position
            ct_byte = ciphertexts[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            result.append(pt_byte)
        else:
            # We don't have keystream for this position
            # This shouldn't happen if the problem is solvable
            result.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(result).hex()
    
    # Output
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == '__main__':
    main()
