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
    
    # This is a stream cipher reuse attack
    # If two messages use the same keystream:
    # C1 = P1 XOR K
    # C2 = P2 XOR K
    # Then: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can recover P2: P2 = P1 XOR C1 XOR C2
    
    # Build a keystream recovery map
    # For each position where we have known plaintext, recover keystream
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        # Find the ciphertext for this message
        ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext:
            # Recover keystream at these positions
            for i, p_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    k_byte = ciphertext[pos] ^ p_byte
                    keystream[pos] = k_byte
    
    # Now recover the target plaintext using the keystream
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = ct['data']
            break
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have keystream at this position, we can't recover it
            # This shouldn't happen with properly specified instances
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
