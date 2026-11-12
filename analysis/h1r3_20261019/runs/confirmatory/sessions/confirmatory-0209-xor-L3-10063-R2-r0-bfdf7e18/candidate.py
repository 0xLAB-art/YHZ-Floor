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
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': data,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    # Get target info
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Build keystream from known plaintexts
    # For each known plaintext: keystream[offset] = ciphertext[offset] XOR plaintext
    max_offset = target_offset + target_length
    keystream = [None] * max_offset
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = kp['data']
        
        # Find corresponding ciphertext
        ct_data = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ct_data = ct['data']
                break
        
        if ct_data:
            for i, pt_byte in enumerate(pt_data):
                pos = offset + i
                if pos < len(ct_data) and pos < max_offset:
                    # keystream[pos] = ct_data[pos] XOR pt_byte
                    ks_byte = ct_data[pos] ^ pt_byte
                    keystream[pos] = ks_byte
    
    # Now decrypt target using recovered keystream
    target_ct = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ct = ct['data']
            break
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream, try to infer from other ciphertexts
            # using crib dragging or statistical analysis
            # For now, we'll try a simple approach
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
