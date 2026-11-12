import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        data = base64.b64decode(ct['data'])
        ciphertexts[idx] = data
    
    # Parse known plaintexts
    known_keystream = {}
    for kp in instance['known_plaintexts']:
        idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        
        # Recover keystream: keystream = ciphertext ⊕ plaintext
        ciphertext = ciphertexts[idx]
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                keystream_byte = ciphertext[pos] ^ p_byte
                known_keystream[pos] = keystream_byte
    
    # Extract target
    target = instance['target']
    target_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Decrypt target using recovered keystream
    target_ciphertext = ciphertexts[target_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in known_keystream and pos < len(target_ciphertext):
            plaintext_byte = target_ciphertext[pos] ^ known_keystream[pos]
            plaintext_bytes.append(plaintext_byte)
        else:
            # Should not happen if the instance is solvable
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
