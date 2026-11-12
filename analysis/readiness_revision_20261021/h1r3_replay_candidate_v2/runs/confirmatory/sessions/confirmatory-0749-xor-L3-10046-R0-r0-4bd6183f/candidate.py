import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ciphertext_bytes = []
    for ct in ciphertexts:
        ciphertext_bytes.append(bytes.fromhex(ct['data']))
    
    # Determine the maximum length needed for keystream
    max_len = max(len(ct) for ct in ciphertext_bytes)
    
    # Initialize keystream as None for each position
    keystream = [None] * max_len
    
    # Recover keystream from known plaintexts
    # K = P ⊕ C
    for kp in known_plaintexts:
        plaintext_data = bytes.fromhex(kp['data'])
        message_index = kp['message_index']
        offset = kp['offset']
        
        ciphertext = ciphertext_bytes[message_index]
        
        # XOR plaintext with ciphertext to get keystream bytes
        for i, p_byte in enumerate(plaintext_data):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = p_byte ^ c_byte
                keystream[pos] = k_byte
    
    # Now decrypt the target using the recovered keystream
    target_message_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_bytes[target_message_index]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have the keystream byte, we can't decrypt
            # This shouldn't happen in a valid instance
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result as JSON
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
