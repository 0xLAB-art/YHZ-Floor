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
        ciphertexts.append({
            'data': base64.b64decode(ct['data']),
            'index': ct['message_index']
        })
    
    # Decode known plaintexts
    known_pts = []
    for kp in instance['known_plaintexts']:
        known_pts.append({
            'data': base64.b64decode(kp['data']),
            'index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find the ciphertext for the target
    target_ct = None
    for ct in ciphertexts:
        if ct['index'] == target_index:
            target_ct = ct['data']
            break
    
    # Build keystream from known plaintexts
    # For stream cipher: C = P XOR K, so K = C XOR P
    keystream = {}
    
    for kp in known_pts:
        msg_index = kp['index']
        offset = kp['offset']
        plaintext = kp['data']
        
        # Find corresponding ciphertext
        ct = None
        for c in ciphertexts:
            if c['index'] == msg_index:
                ct = c['data']
                break
        
        if ct:
            # Extract keystream bytes
            for i, p_byte in enumerate(plaintext):
                pos = offset + i
                if pos < len(ct):
                    k_byte = ct[pos] ^ p_byte
                    keystream[pos] = k_byte
    
    # Decrypt target using recovered keystream
    result = bytearray()
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            plaintext_byte = target_ct[pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # If keystream byte is unknown, we cannot decrypt
            # Try to recover it from other messages
            # For now, append 0 as placeholder
            result.append(0)
    
    # Output
    output = {
        "plaintext": result.hex()
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()