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
        idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        if idx not in known_plaintexts:
            known_plaintexts[idx] = {}
        known_plaintexts[idx][offset] = plaintext
    
    # Get target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Stream cipher attack: C = P XOR K
    # If we know P0 and C0, we can recover K: K = P0 XOR C0
    # Then we can decrypt any other ciphertext: P1 = C1 XOR K
    
    # Find a known plaintext that overlaps with our target
    for known_idx, known_data in known_plaintexts.items():
        for known_offset, known_plaintext in known_data.items():
            # Get the corresponding ciphertext section
            c_known = ciphertexts[known_idx][known_offset:known_offset + len(known_plaintext)]
            
            # Recover the keystream
            keystream = xor_bytes(known_plaintext, c_known)
            
            # Now decrypt the target using the same keystream
            c_target = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
            
            # The keystream should be the same at the same positions
            # assuming stream cipher reuse
            if len(keystream) >= target_length:
                plaintext = xor_bytes(c_target, keystream[:target_length])
                result = {"plaintext": plaintext.hex()}
                print(json.dumps(result))
                return
    
    # If we get here, something went wrong
    print(json.dumps({"plaintext": "00" * target_length}))

if __name__ == "__main__":
    main()