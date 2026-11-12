import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Build keystream from known plaintexts
    # For stream cipher: ciphertext XOR plaintext = keystream
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            c_byte = ciphertexts[msg_idx][pos]
            k_byte = c_byte ^ p_byte
            
            if pos not in keystream:
                keystream[pos] = k_byte
            elif keystream[pos] != k_byte:
                # Inconsistency check (shouldn't happen with valid data)
                pass
    
    # Extract target plaintext
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            c_byte = ciphertexts[target_msg_idx][pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If keystream byte is unknown, we can't decrypt
            # This shouldn't happen based on the problem setup
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()