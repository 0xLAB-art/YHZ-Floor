import sys
import json
import base64
from collections import defaultdict

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
            'index': ct['message_index']
        })
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': data,
            'index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target_index = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Build keystream recovery map
    # For stream cipher reuse: P1 XOR P2 = C1 XOR C2
    # If we know P1, we can find K = P1 XOR C1, then P2 = K XOR C2
    
    keystream = {}  # position -> keystream byte
    
    # Extract keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        # Find corresponding ciphertext
        ciphertext = None
        for ct in ciphertexts:
            if ct['index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext:
            for i, p_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    k_byte = p_byte ^ ciphertext[pos]
                    keystream[pos] = k_byte
    
    # Recover target plaintext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['index'] == target_index:
            target_ciphertext = ct['data']
            break
    
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            p_byte = keystream[pos] ^ target_ciphertext[pos]
            result.append(p_byte)
        else:
            # If we don't have keystream, try to derive from other messages
            # using ciphertext XOR relationships
            found = False
            
            # Try all pairs of messages where we know plaintext at this position
            for kp in known_plaintexts:
                kp_offset = kp['offset']
                kp_len = len(kp['data'])
                if kp_offset <= pos < kp_offset + kp_len:
                    # We know plaintext for message kp['index'] at position pos
                    kp_msg_idx = kp['index']
                    kp_plaintext_byte = kp['data'][pos - kp_offset]
                    
                    # Get ciphertext for that message
                    kp_ciphertext = None
                    for ct in ciphertexts:
                        if ct['index'] == kp_msg_idx:
                            kp_ciphertext = ct['data']
                            break
                    
                    if kp_ciphertext and pos < len(kp_ciphertext):
                        # Recover keystream: K = P XOR C
                        k_byte = kp_plaintext_byte ^ kp_ciphertext[pos]
                        keystream[pos] = k_byte
                        
                        # Now decrypt target
                        if pos < len(target_ciphertext):
                            p_byte = k_byte ^ target_ciphertext[pos]
                            result.append(p_byte)
                            found = True
                            break
            
            if not found:
                result.append(0)  # fallback
    
    plaintext_hex = bytes(result).hex()
    
    output = {
        "plaintext": plaintext_hex
    }
    
    print(json.dumps(output))

if __name__ == '__main__':
    main()
