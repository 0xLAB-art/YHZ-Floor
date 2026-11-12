import sys
import json
import base64

def main():
    # Read instance
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
        plaintext_bytes = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': plaintext_bytes,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_message_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Build a mapping from message_index to ciphertext
    ciphertext_map = {ct['message_index']: ct['data'] for ct in ciphertexts}
    
    # Recover keystream bytes using known plaintexts
    # In a stream cipher: C = P XOR K, so K = P XOR C
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['data']
        
        if msg_idx not in ciphertext_map:
            continue
            
        ciphertext = ciphertext_map[msg_idx]
        
        # Extract keystream bytes
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = p_byte ^ c_byte
                keystream[pos] = k_byte
    
    # Now decrypt the target using recovered keystream
    target_ciphertext = ciphertext_map[target_message_index]
    plaintext_bytes = bytearray()
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            c_byte = target_ciphertext[pos]
            k_byte = keystream[pos]
            p_byte = c_byte ^ k_byte
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = plaintext_bytes.hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()