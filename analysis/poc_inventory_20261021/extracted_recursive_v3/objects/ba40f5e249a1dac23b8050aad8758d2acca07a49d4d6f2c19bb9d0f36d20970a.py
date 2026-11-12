import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    # Parse known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': data,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    # Target
    target_msg = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Build keystream recovery
    # Find max length needed
    max_pos = target_offset + target_length
    keystream = [None] * max_pos
    
    # Recover keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = kp['data']
        
        # Find the ciphertext for this message
        ct_data = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ct_data = ct['data']
                break
        
        if ct_data is None:
            continue
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(ct_data):
                keystream[pos] = pt_byte ^ ct_data[pos]
    
    # Find target ciphertext
    target_ct = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg:
            target_ct = ct['data']
            break
    
    # Decrypt target using recovered keystream
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(keystream) and keystream[pos] is not None and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # If we don't have keystream, we can't decrypt
            # This shouldn't happen if the challenge is solvable
            plaintext.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext).hex()
    
    # Output
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()