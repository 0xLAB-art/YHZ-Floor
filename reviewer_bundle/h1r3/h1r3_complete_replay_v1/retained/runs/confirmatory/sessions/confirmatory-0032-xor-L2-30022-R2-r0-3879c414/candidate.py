import sys
import json
import base64

def main():
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
    known = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known.append({
            'data': data,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find ciphertext for target message
    target_ct = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ct = ct['data']
            break
    
    # Recover keystream bytes using known plaintexts
    keystream = {}
    
    for kp in known:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['data']
        
        # Find the ciphertext for this message
        ct_data = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ct_data = ct['data']
                break
        
        if ct_data is None:
            continue
        
        # Recover keystream: K = P ⊕ C
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ct_data):
                k_byte = p_byte ^ ct_data[pos]
                keystream[pos] = k_byte
    
    # Decrypt target using recovered keystream
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            plaintext_byte = target_ct[pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen if the problem is solvable
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    output = {'plaintext': plaintext_hex}
    print(json.dumps(output))

if __name__ == '__main__':
    main()
