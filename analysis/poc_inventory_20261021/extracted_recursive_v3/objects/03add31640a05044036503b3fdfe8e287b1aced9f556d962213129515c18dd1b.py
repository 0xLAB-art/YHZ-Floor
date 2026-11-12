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
    
    # Parse input
    ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = hex_to_bytes(kp['data'])
        if msg_idx not in known_plaintexts:
            known_plaintexts[msg_idx] = {}
        known_plaintexts[msg_idx][offset] = data
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Recover keystream from known plaintext
    # For message 0, we have plaintext and ciphertext
    known_msg_idx = 0
    known_offset = 0
    known_plaintext = known_plaintexts[known_msg_idx][known_offset]
    known_ciphertext = ciphertexts[known_msg_idx][known_offset:known_offset + len(known_plaintext)]
    
    # Recover keystream: keystream = plaintext XOR ciphertext
    keystream = xor_bytes(known_plaintext, known_ciphertext)
    
    # Decrypt target using recovered keystream
    # Assuming same keystream is reused (stream cipher nonce reuse attack)
    target_ciphertext = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
    
    # If keystream is long enough, use it directly
    if len(keystream) >= target_length:
        plaintext = xor_bytes(target_ciphertext, keystream[:target_length])
    else:
        # If not enough keystream, we can only decrypt what we have
        plaintext = xor_bytes(target_ciphertext[:len(keystream)], keystream)
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(plaintext)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()