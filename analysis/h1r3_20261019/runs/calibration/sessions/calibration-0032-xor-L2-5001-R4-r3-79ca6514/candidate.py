import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # Build a keystream recovery map
    # For stream cipher: ciphertext[i] = plaintext[i] XOR keystream[i]
    # So: keystream[i] = plaintext[i] XOR ciphertext[i]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            ct_byte = ct_bytes[msg_idx][pos]
            key_byte = pt_byte ^ ct_byte
            keystream[pos] = key_byte
    
    # Recover target plaintext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            result.append(pt_byte)
        else:
            # If keystream not known, we cannot recover (should not happen with valid input)
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
