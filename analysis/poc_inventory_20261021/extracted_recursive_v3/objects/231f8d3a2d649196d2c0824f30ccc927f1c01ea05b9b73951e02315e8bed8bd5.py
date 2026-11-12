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
    
    # Extract keystream from known plaintext
    # For message 0, we know plaintext at offset 0
    known_msg_idx = 0
    known_offset = 0
    known_plaintext = known_plaintexts[known_msg_idx][known_offset]
    known_ciphertext = ciphertexts[known_msg_idx]
    
    # Extract keystream: keystream = plaintext XOR ciphertext
    keystream_start = known_offset
    keystream = xor_bytes(known_plaintext, known_ciphertext[known_offset:known_offset + len(known_plaintext)])
    
    # Use keystream to decrypt target
    target_ciphertext = ciphertexts[target_msg_idx]
    target_plaintext = xor_bytes(
        keystream[target_offset:target_offset + target_length],
        target_ciphertext[target_offset:target_offset + target_length]
    )
    
    result = {
        "plaintext": target_plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()