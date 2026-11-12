import json
import sys
import base64

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        data = base64.b64decode(ct['data'])
        ciphertexts[idx] = data
    
    # Parse known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        idx = kp['message_index']
        offset = kp['offset']
        data = base64.b64decode(kp['data'])
        if idx not in known_plaintexts:
            known_plaintexts[idx] = {}
        known_plaintexts[idx][offset] = data
    
    # Parse target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # This is a stream cipher reuse attack
    # If C0 = P0 XOR K and C1 = P1 XOR K (same keystream K)
    # Then C0 XOR P0 = K, and K XOR C1 = P1
    
    # Find a known plaintext for message 0
    known_msg_idx = 0
    known_offset = 0
    known_plaintext = known_plaintexts[known_msg_idx][known_offset]
    
    # Extract the keystream from the known plaintext
    ciphertext_0 = ciphertexts[known_msg_idx]
    keystream = xor_bytes(ciphertext_0[known_offset:known_offset + len(known_plaintext)], known_plaintext)
    
    # Use the keystream to decrypt the target
    ciphertext_target = ciphertexts[target_msg_idx]
    target_ciphertext_slice = ciphertext_target[target_offset:target_offset + target_length]
    
    # Decrypt using the keystream
    plaintext = xor_bytes(target_ciphertext_slice, keystream[:target_length])
    
    # Convert to hex
    plaintext_hex = plaintext.hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
