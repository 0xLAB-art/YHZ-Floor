import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append(data)
    
    # Recover key stream from known plaintexts
    # key_stream[position] = byte value at that position
    key_stream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        ciphertext = ciphertexts[msg_idx]
        
        # Recover key stream bytes
        for i, pt_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                key_byte = ciphertext[pos] ^ pt_byte
                key_stream[pos] = key_byte
    
    # Decrypt target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in key_stream and pos < len(target_ciphertext):
            pt_byte = target_ciphertext[pos] ^ key_stream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have the key byte, we need to try to recover it
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
