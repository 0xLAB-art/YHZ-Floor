import json
import sys
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': base64.b64decode(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Decode known plaintexts
    known = []
    for kp in instance['known_plaintexts']:
        known.append({
            'data': base64.b64decode(kp['data']),
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find the target ciphertext
    target_ct = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ct = ct['data']
            break
    
    # Stream cipher attack: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can get P2 = (C1 XOR C2) XOR P1
    
    # Build a keystream recovery map
    keystream = {}
    
    # For each known plaintext, recover keystream bytes
    for kp in known:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['data']
        
        # Find the ciphertext for this message
        ct = None
        for c in ciphertexts:
            if c['message_index'] == msg_idx:
                ct = c['data']
                break
        
        if ct:
            # Recover keystream: K = P XOR C
            for i, p_byte in enumerate(plaintext):
                pos = offset + i
                if pos < len(ct):
                    k_byte = p_byte ^ ct[pos]
                    keystream[pos] = k_byte
    
    # Now decrypt the target using the recovered keystream
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            plaintext_byte = target_ct[pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # If we don't have the keystream, we need to derive it
            # Try to find another message with known plaintext at this position
            # and use the XOR relationship
            found = False
            
            # For each pair of messages where one has known plaintext at pos
            for kp in known:
                kp_msg_idx = kp['message_index']
                kp_offset = kp['offset']
                kp_data = kp['data']
                
                # Check if this known plaintext covers position pos
                if kp_offset <= pos < kp_offset + len(kp_data):
                    # We know plaintext at position pos for message kp_msg_idx
                    kp_plaintext_byte = kp_data[pos - kp_offset]
                    
                    # Find ciphertext for this message
                    kp_ct = None
                    for c in ciphertexts:
                        if c['message_index'] == kp_msg_idx:
                            kp_ct = c['data']
                            break
                    
                    if kp_ct and pos < len(kp_ct):
                        # Recover keystream
                        k_byte = kp_plaintext_byte ^ kp_ct[pos]
                        keystream[pos] = k_byte
                        
                        # Decrypt target
                        if pos < len(target_ct):
                            plaintext_byte = target_ct[pos] ^ k_byte
                            result.append(plaintext_byte)
                            found = True
                            break
            
            if not found:
                result.append(0)
    
    plaintext_hex = bytes(result).hex()
    
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
