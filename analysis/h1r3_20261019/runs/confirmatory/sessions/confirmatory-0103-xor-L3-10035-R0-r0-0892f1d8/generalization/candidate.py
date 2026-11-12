import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # Recover keystream from known plaintexts
    # We need keystream for positions target['offset'] to target['offset'] + target['length']
    target_start = target['offset']
    target_end = target['offset'] + target['length']
    
    # Initialize keystream as None for unknown positions
    keystream = {}
    
    # For each known plaintext, recover the keystream
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        # Get corresponding ciphertext bytes
        ct_data = ct_bytes[msg_idx][offset:offset + len(pt_data)]
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i in range(len(pt_data)):
            pos = offset + i
            ks_byte = pt_data[i] ^ ct_data[i]
            keystream[pos] = ks_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_ct = ct_bytes[target_msg_idx][target_start:target_end]
    
    plaintext = []
    for i in range(target['length']):
        pos = target_start + i
        if pos in keystream:
            pt_byte = target_ct[i] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # If we don't have keystream at this position, this is a problem
            # But based on the problem structure, we should have enough known plaintexts
            raise ValueError(f"Missing keystream at position {pos}")
    
    # Convert plaintext to hex
    plaintext_hex = bytes(plaintext).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
