import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Decode known plaintexts
    known = []
    for kp in instance['known_plaintexts']:
        known.append({
            'data': base64.b64decode(kp['data']),
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Stream cipher reuse attack
    # If C1 = P1 XOR K and C2 = P2 XOR K, then C1 XOR C2 = P1 XOR P2
    # If we know P1, we can compute K = C1 XOR P1, then P2 = C2 XOR K
    
    # Build keystream from known plaintexts
    max_len = max(len(ct) for ct in ciphertexts)
    keystream = [None] * max_len
    
    for kp in known:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['data']
        ciphertext = ciphertexts[msg_idx]
        
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                k_byte = ciphertext[pos] ^ p_byte
                if keystream[pos] is None:
                    keystream[pos] = k_byte
                elif keystream[pos] != k_byte:
                    # Consistency check - should not happen with correct data
                    pass
    
    # Extract target plaintext using recovered keystream
    target_ciphertext = ciphertexts[target_msg]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # Should not happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()