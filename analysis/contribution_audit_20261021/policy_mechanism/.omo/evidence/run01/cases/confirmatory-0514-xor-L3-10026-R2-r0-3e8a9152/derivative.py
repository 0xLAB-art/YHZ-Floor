import sys
import json
import base64


def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
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
        plaintext = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': plaintext,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Build keystream recovery map
    # keystream[position] = keystream_byte
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['data']
        ciphertext = ciphertexts[msg_idx]['data']
        
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            c_byte = ciphertext[pos]
            k_byte = c_byte ^ p_byte
            keystream[pos] = k_byte
    
    # Recover target plaintext
    target_ciphertext = ciphertexts[target_msg_idx]['data']
    target_plaintext = bytearray()
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            target_plaintext.append(p_byte)
        else:
            # Missing keystream - try to infer from other messages
            # This is a stream cipher reuse attack
            # Try XOR with other ciphertexts at same position
            
            # Use crib-dragging or frequency analysis
            # For now, try common bytes
            found = False
            
            # Try XORing with all other messages to find patterns
            for other_idx in range(len(ciphertexts)):
                if other_idx == target_msg_idx:
                    continue
                
                other_ct = ciphertexts[other_idx]['data']
                if pos < len(other_ct):
                    xor_result = target_ciphertext[pos] ^ other_ct[pos]
                    
                    # Check if this XOR looks like plaintext XOR plaintext
                    # Common case: space (0x20) XOR letter gives letter ^ 0x20
                    
                    # Try assuming space in one message
                    for test_char in [0x20, 0x65, 0x61, 0x6f, 0x69, 0x74, 0x6e, 0x73]:  # space, e, a, o, i, t, n, s
                        k_byte_candidate = other_ct[pos] ^ test_char
                        p_byte_candidate = target_ciphertext[pos] ^ k_byte_candidate
                        
                        # Check if reasonable ASCII
                        if 0x20 <= p_byte_candidate <= 0x7e:
                            if not found:
                                keystream[pos] = k_byte_candidate
                                target_plaintext.append(p_byte_candidate)
                                found = True
                                break
                    
                    if found:
                        break
            
            if not found:
                # Default to 0x20 (space) if nothing else works
                target_plaintext.append(0x20)
    
    # Convert to hex
    result = target_plaintext.hex()
    
    print(json.dumps({"plaintext": result}))

if __name__ == "__main__":
    main()
