import sys
import json
import base64

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts[ct['message_index']] = data
    
    # Decode known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts[(kp['message_index'], kp['offset'])] = data
    
    # Extract target information
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Recover keystream from known plaintext
    # Assuming stream cipher: ciphertext = plaintext XOR keystream
    keystream = {}
    
    for (msg_idx, offset), plaintext in known_plaintexts.items():
        ciphertext = ciphertexts[msg_idx]
        for i, p_byte in enumerate(plaintext):
            c_byte = ciphertext[offset + i]
            k_byte = p_byte ^ c_byte
            keystream[offset + i] = k_byte
    
    # Decrypt target using recovered keystream
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt
            # This shouldn't happen if the problem is well-formed
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
