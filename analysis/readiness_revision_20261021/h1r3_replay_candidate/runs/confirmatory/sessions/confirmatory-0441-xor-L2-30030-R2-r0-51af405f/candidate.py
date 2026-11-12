import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append((ct['message_index'], data))
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts.append((kp['message_index'], kp['offset'], data))
    
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Find ciphertext for target
    target_ciphertext = None
    for msg_idx, ct in ciphertexts:
        if msg_idx == target_msg_idx:
            target_ciphertext = ct
            break
    
    # Build keystream from known plaintexts
    max_len = max(len(ct) for _, ct in ciphertexts)
    keystream = [None] * max_len
    
    for msg_idx, offset, plaintext in known_plaintexts:
        # Find corresponding ciphertext
        ciphertext = None
        for ct_idx, ct in ciphertexts:
            if ct_idx == msg_idx:
                ciphertext = ct
                break
        
        if ciphertext is None:
            continue
        
        # XOR to recover keystream
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = p_byte ^ c_byte
                if keystream[pos] is None:
                    keystream[pos] = k_byte
                elif keystream[pos] != k_byte:
                    # Conflict - shouldn't happen with correct data
                    pass
    
    # Decrypt target using recovered keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If keystream not recovered at this position, we have a problem
            # Try to infer from crib dragging or assume 0
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
