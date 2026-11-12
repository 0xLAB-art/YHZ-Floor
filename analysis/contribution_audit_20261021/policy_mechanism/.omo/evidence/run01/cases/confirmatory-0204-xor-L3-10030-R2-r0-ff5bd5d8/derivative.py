import sys
import json
import base64


def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Decode all ciphertexts from base64
    decoded_ciphertexts = []
    for ct in ciphertexts:
        decoded_ciphertexts.append(base64.b64decode(ct['data']))
    
    # This is a many-time pad attack
    # When the same key stream is reused, we can XOR ciphertexts together
    # and use known plaintexts to recover the key stream
    
    # First, recover the key stream using known plaintexts
    # key_stream[position] = ciphertext[position] XOR plaintext[position]
    key_stream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        ciphertext = decoded_ciphertexts[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            position = offset + i
            if position < len(ciphertext):
                # Recover key stream byte at this position
                key_byte = ciphertext[position] ^ pt_byte
                
                # Store or verify consistency
                if position in key_stream:
                    # Verify consistency
                    if key_stream[position] != key_byte:
                        # Inconsistency - shouldn't happen with correct data
                        pass
                else:
                    key_stream[position] = key_byte
    
    # Now decrypt the target using the recovered key stream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = decoded_ciphertexts[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        position = target_offset + i
        if position in key_stream and position < len(target_ciphertext):
            pt_byte = target_ciphertext[position] ^ key_stream[position]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have the key stream at this position, we need to derive it
            # This shouldn't happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
