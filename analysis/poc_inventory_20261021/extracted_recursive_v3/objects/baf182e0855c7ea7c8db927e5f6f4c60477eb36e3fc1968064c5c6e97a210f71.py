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
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # This is a stream cipher reuse attack (likely XOR with same keystream)
    # If C1 = P1 XOR K and C2 = P2 XOR K, then C1 XOR C2 = P1 XOR P2
    # If we know P1, we can recover P2 = P1 XOR C1 XOR C2
    
    # Build a keystream by recovering it from known plaintexts
    max_len = max(len(ct['data']) for ct in ciphertexts)
    keystream = [None] * max_len
    
    # Extract keystream bytes from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['data']
        
        # Find the ciphertext for this message
        ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext:
            # Recover keystream: K = P XOR C
            for i, p_byte in enumerate(plaintext):
                pos = offset + i
                if pos < len(ciphertext):
                    c_byte = ciphertext[pos]
                    k_byte = p_byte ^ c_byte
                    keystream[pos] = k_byte
    
    # Now decrypt the target using the recovered keystream
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = ct['data']
            break
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have the keystream byte, we need to infer it
            # Try to use relationships between ciphertexts
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()