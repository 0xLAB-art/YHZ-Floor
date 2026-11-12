import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': base64.b64decode(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        known_plaintexts.append({
            'data': base64.b64decode(kp['data']),
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    # Extract target information
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # This is a stream cipher reuse attack (many-time pad)
    # If two messages use the same keystream: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can recover P2: P2 = P1 XOR C1 XOR C2
    
    # Build a keystream recovery map
    keystream = {}
    
    # For each known plaintext, recover the keystream at those positions
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        ct = ciphertexts[msg_idx]['data']
        
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct):
                k_byte = ct[pos] ^ p_byte
                keystream[pos] = k_byte
    
    # Now recover the target plaintext using the keystream
    target_ct = ciphertexts[target_msg_idx]['data']
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            p_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have keystream at this position, try XOR with other messages
            # Use known plaintexts from other messages at the same position
            recovered = False
            for kp in known_plaintexts:
                if kp['offset'] <= pos < kp['offset'] + len(kp['data']):
                    # This known plaintext covers this position
                    kp_msg_idx = kp['message_index']
                    kp_offset_in_plaintext = pos - kp['offset']
                    kp_plaintext_byte = kp['data'][kp_offset_in_plaintext]
                    
                    # P_target = P_kp XOR C_kp XOR C_target
                    c_kp = ciphertexts[kp_msg_idx]['data'][pos]
                    c_target = target_ct[pos]
                    p_target = kp_plaintext_byte ^ c_kp ^ c_target
                    plaintext_bytes.append(p_target)
                    recovered = True
                    break
            
            if not recovered:
                plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
