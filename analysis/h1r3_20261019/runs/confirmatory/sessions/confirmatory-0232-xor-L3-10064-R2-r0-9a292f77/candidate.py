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
    
    # Build a keystream recovery map
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        # XOR ciphertext with plaintext to get keystream
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            ct_byte = ciphertexts[msg_idx][pos]
            ks_byte = ct_byte ^ pt_byte
            
            # Store keystream byte at this position
            if pos not in keystream:
                keystream[pos] = ks_byte
    
    # Extract target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Decrypt target using recovered keystream
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = ciphertexts[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            result.append(pt_byte)
        else:
            # If keystream not known at this position, we have a problem
            # But based on the problem structure, all positions should be covered
            result.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(result).hex()
    
    # Output
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()
