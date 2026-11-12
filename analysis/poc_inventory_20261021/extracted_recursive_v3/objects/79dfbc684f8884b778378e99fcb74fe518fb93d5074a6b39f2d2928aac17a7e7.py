import sys
import json
import base64

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts[ct['message_index']] = data
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts[(kp['message_index'], kp['offset'])] = data
    
    target = instance['target']
    target_message_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Extract keystream from known plaintext-ciphertext pairs
    # We'll build a keystream for the positions we know
    keystream = {}
    
    for (msg_idx, offset), plaintext_data in known_plaintexts.items():
        if msg_idx in ciphertexts:
            ciphertext_data = ciphertexts[msg_idx]
            # XOR plaintext with ciphertext to get keystream
            for i, plain_byte in enumerate(plaintext_data):
                pos = offset + i
                if pos < len(ciphertext_data):
                    cipher_byte = ciphertext_data[pos]
                    keystream_byte = plain_byte ^ cipher_byte
                    keystream[pos] = keystream_byte
    
    # Now decrypt the target using the recovered keystream
    if target_message_index in ciphertexts:
        target_ciphertext = ciphertexts[target_message_index]
        plaintext_bytes = bytearray()
        
        for i in range(target_length):
            pos = target_offset + i
            if pos in keystream and pos < len(target_ciphertext):
                cipher_byte = target_ciphertext[pos]
                plain_byte = cipher_byte ^ keystream[pos]
                plaintext_bytes.append(plain_byte)
            else:
                # If we don't have keystream for this position, we can't decrypt
                # This shouldn't happen if the challenge is solvable
                plaintext_bytes.append(0)
        
        # Convert to hex
        plaintext_hex = plaintext_bytes.hex()
        
        # Output the result
        result = {"plaintext": plaintext_hex}
        print(json.dumps(result))
    else:
        # Target message not found
        result = {"plaintext": "00" * target_length}
        print(json.dumps(result))

if __name__ == "__main__":
    main()