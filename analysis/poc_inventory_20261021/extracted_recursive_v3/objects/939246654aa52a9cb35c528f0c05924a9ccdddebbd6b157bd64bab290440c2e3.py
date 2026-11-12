import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Recover keystream from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_data = bytes.fromhex(kp['data'])
        
        # XOR ciphertext with known plaintext to get keystream
        for i, pt_byte in enumerate(plaintext_data):
            pos = offset + i
            ct_byte = ct_bytes[msg_idx][pos]
            ks_byte = ct_byte ^ pt_byte
            keystream[pos] = ks_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We have the keystream byte, decrypt it
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # We don't have this keystream byte
            # This shouldn't happen if the problem is solvable
            plaintext.append(0)
    
    plaintext_hex = bytes(plaintext).hex()
    
    result = {
        "plaintext": plaintext_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()