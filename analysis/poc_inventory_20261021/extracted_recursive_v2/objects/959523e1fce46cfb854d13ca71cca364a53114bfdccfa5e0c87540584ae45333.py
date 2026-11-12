import sys
import json
import base64

def main():
    # Read instance from command line argument
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
    
    # Build keystream using known plaintexts and XOR property
    # For stream cipher: C = P XOR K, so K = P XOR C
    max_length = max(len(ct['data']) for ct in ciphertexts)
    keystream = [None] * max_length
    
    # Extract keystream bytes from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        # Find the corresponding ciphertext
        ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext:
            for i, p_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    k_byte = p_byte ^ ciphertext[pos]
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
            # If we don't have the keystream byte, we have a problem
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    # Convert to hex string
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
