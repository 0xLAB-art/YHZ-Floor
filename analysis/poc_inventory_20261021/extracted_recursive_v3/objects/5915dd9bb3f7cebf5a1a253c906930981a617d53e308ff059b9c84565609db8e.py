import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    target = instance['target']
    ciphertexts = {ct['message_index']: ct['data'] for ct in instance['ciphertexts']}
    known_plaintexts = {kp['message_index']: {'offset': kp['offset'], 'data': kp['data']} 
                        for kp in instance['known_plaintexts']}
    
    # This is a many-time pad attack
    # We have ciphertext for message 0 and its plaintext
    # We can recover the keystream used for message 0
    # If the same keystream is reused for message 1, we can decrypt it
    
    # Get known plaintext for message 0
    known_msg_idx = 0
    known_plaintext_hex = known_plaintexts[known_msg_idx]['data']
    known_offset = known_plaintexts[known_msg_idx]['offset']
    
    # Get ciphertext for message 0
    ciphertext_0_hex = ciphertexts[known_msg_idx]
    
    # Convert to bytes
    known_plaintext = bytes.fromhex(known_plaintext_hex)
    ciphertext_0 = bytes.fromhex(ciphertext_0_hex)
    
    # Recover keystream: keystream = plaintext XOR ciphertext
    keystream = bytes(p ^ c for p, c in zip(known_plaintext, ciphertext_0))
    
    # Get target ciphertext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    ciphertext_target_hex = ciphertexts[target_msg_idx]
    ciphertext_target = bytes.fromhex(ciphertext_target_hex)
    
    # Extract the portion we need to decrypt
    ciphertext_portion = ciphertext_target[target_offset:target_offset + target_length]
    keystream_portion = keystream[target_offset:target_offset + target_length]
    
    # Decrypt: plaintext = ciphertext XOR keystream
    plaintext = bytes(c ^ k for c, k in zip(ciphertext_portion, keystream_portion))
    
    # Convert to hex
    plaintext_hex = plaintext.hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()