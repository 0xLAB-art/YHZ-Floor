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
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Recover keystream
    # keystream[message_index][position] = byte
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        if msg_idx not in keystream:
            keystream[msg_idx] = {}
        
        # Find corresponding ciphertext
        ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext:
            for i, pt_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    # keystream = plaintext XOR ciphertext
                    ks_byte = pt_byte ^ ciphertext[pos]
                    keystream[msg_idx][pos] = ks_byte
    
    # Check if this is a reused keystream attack (many-time pad)
    # Try to see if keystream is reused across messages
    # Collect all keystream bytes by position across all messages
    keystream_by_position = {}
    for msg_idx in keystream:
        for pos, ks_byte in keystream[msg_idx].items():
            if pos not in keystream_by_position:
                keystream_by_position[pos] = {}
            keystream_by_position[pos][msg_idx] = ks_byte
    
    # Check if keystream is the same across different messages at same position
    # This would indicate keystream reuse (many-time pad)
    reused_keystream = {}
    for pos in keystream_by_position:
        if len(keystream_by_position[pos]) > 1:
            # Multiple messages have keystream at this position
            # Check if they're all the same
            values = list(keystream_by_position[pos].values())
            if len(set(values)) == 1:
                # All same - keystream is reused
                reused_keystream[pos] = values[0]
            else:
                # Different values - keystream is NOT reused, it's per-message
                pass
    
    # If we found reused keystream, use it
    if reused_keystream:
        # Keystream reuse scenario
        target_ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == target_msg_idx:
                target_ciphertext = ct['data']
                break
        
        plaintext_bytes = []
        for i in range(target_length):
            pos = target_offset + i
            if pos in reused_keystream and pos < len(target_ciphertext):
                pt_byte = target_ciphertext[pos] ^ reused_keystream[pos]
                plaintext_bytes.append(pt_byte)
            else:
                # Can't decrypt this byte
                plaintext_bytes.append(0)
        
        plaintext_hex = bytes(plaintext_bytes).hex()
    else:
        # Per-message keystream scenario
        target_ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == target_msg_idx:
                target_ciphertext = ct['data']
                break
        
        if target_msg_idx in keystream:
            plaintext_bytes = []
            for i in range(target_length):
                pos = target_offset + i
                if pos in keystream[target_msg_idx] and pos < len(target_ciphertext):
                    pt_byte = target_ciphertext[pos] ^ keystream[target_msg_idx][pos]
                    plaintext_bytes.append(pt_byte)
                else:
                    plaintext_bytes.append(0)
            
            plaintext_hex = bytes(plaintext_bytes).hex()
        else:
            plaintext_hex = '00' * target_length
    
    # Output
    result = {'plaintext': plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()