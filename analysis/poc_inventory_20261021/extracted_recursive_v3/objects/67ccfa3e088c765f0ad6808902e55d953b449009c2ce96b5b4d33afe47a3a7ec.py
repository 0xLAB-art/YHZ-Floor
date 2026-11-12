import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(base64.b64decode(ct['data']))
    
    # Find the maximum offset we need
    target_start = instance['target']['offset']
    target_length = instance['target']['length']
    target_end = target_start + target_length
    target_msg_idx = instance['target']['message_index']
    
    # Build keystream from known plaintexts
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        # Extract keystream: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertexts[msg_idx][pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target using recovered keystream
    target_plaintext = bytearray()
    for pos in range(target_start, target_end):
        if pos in keystream:
            # Decrypt: plaintext = ciphertext XOR keystream
            ct_byte = ciphertexts[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            target_plaintext.append(pt_byte)
        else:
            # No keystream available for this position - this shouldn't happen
            # if the problem is solvable, but handle gracefully
            target_plaintext.append(0)
    
    # Output result as lowercase hex
    result = {
        "plaintext": target_plaintext.hex()
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()