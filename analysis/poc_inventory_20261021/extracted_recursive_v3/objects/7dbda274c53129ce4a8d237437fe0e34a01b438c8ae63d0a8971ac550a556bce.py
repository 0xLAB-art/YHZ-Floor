import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse input
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': data,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find the ciphertext for the target message
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = ct['data']
            break
    
    # This is a many-time pad attack
    # We have multiple messages encrypted with the same keystream (stream cipher reuse)
    # We can recover the keystream using known plaintexts, then decrypt the target
    
    # Determine the maximum length we need
    max_len = max(len(ct['data']) for ct in ciphertexts)
    
    # Initialize keystream recovery (None means unknown)
    keystream = [None] * max_len
    
    # Recover keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        # Find the corresponding ciphertext
        ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext is None:
            continue
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = p_byte ^ c_byte
                
                # Store the keystream byte
                if keystream[pos] is None:
                    keystream[pos] = k_byte
                elif keystream[pos] != k_byte:
                    # Inconsistency - but we'll trust the first one or latest
                    pass
    
    # Now decrypt the target using the recovered keystream
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext.append(p_byte)
        else:
            # If we don't have the keystream, we need to infer it
            # For now, use 0 as placeholder (this shouldn't happen with enough known plaintexts)
            plaintext.append(0)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext)
    
    # Output
    result = {'plaintext': plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()