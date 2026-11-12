import sys
import json
import base64

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = base64.b64decode(ct['data'])
    
    # Parse known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        if kp['message_index'] not in known_plaintexts:
            known_plaintexts[kp['message_index']] = {}
        known_plaintexts[kp['message_index']][kp['offset']] = base64.b64decode(kp['data'])
    
    # Parse target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Stream cipher attack: if we know plaintext P0 and ciphertext C0 at some position,
    # we can recover keystream K = P0 XOR C0
    # Then use K to decrypt other ciphertext C1 = P1 XOR K, so P1 = C1 XOR K
    
    # Find known plaintext for message 0 at offset 0
    known_msg_idx = 0
    known_offset = 0
    known_plaintext = known_plaintexts[known_msg_idx][known_offset]
    
    # Get corresponding ciphertext
    known_ciphertext = ciphertexts[known_msg_idx][known_offset:known_offset + len(known_plaintext)]
    
    # Recover keystream
    keystream = xor_bytes(known_plaintext, known_ciphertext)
    
    # Decrypt target
    target_ciphertext = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
    target_plaintext = xor_bytes(target_ciphertext, keystream[:target_length])
    
    # Output result
    result = {
        "plaintext": target_plaintext.hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
