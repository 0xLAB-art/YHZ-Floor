import sys
import json

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        data = hex_to_bytes(ct['data'])
        ciphertexts[idx] = data
    
    # Determine maximum length needed
    max_len = max(len(ct) for ct in ciphertexts.values())
    
    # Initialize keystream recovery array (None means unknown)
    keystream = [None] * max_len
    
    # Process known plaintexts to recover keystream
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        # Get corresponding ciphertext
        ciphertext = ciphertexts[msg_idx]
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                ct_byte = ciphertext[pos]
                ks_byte = pt_byte ^ ct_byte
                keystream[pos] = ks_byte
    
    # Extract target information
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Decrypt target using recovered keystream
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream, we can't decrypt - this shouldn't happen
            # with a well-formed instance, but handle gracefully
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes_to_hex(bytes(plaintext_bytes))
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()