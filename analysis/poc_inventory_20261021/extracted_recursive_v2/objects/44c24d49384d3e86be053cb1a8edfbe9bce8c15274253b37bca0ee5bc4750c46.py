import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        ct_data[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Convert known plaintexts to bytes
    kp_data = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = bytes.fromhex(kp['data'])
        if msg_idx not in kp_data:
            kp_data[msg_idx] = {}
        for i, b in enumerate(plaintext):
            kp_data[msg_idx][offset + i] = b
    
    # This is a stream cipher reuse attack (likely XOR with same keystream)
    # For each position, if we know plaintext P at position i for message m:
    # C_m[i] = P_m[i] XOR K[i]
    # Therefore K[i] = C_m[i] XOR P_m[i]
    # Then for target message t: P_t[i] = C_t[i] XOR K[i]
    
    keystream = {}
    
    # Recover keystream from known plaintexts
    for msg_idx, positions in kp_data.items():
        for pos, plaintext_byte in positions.items():
            ciphertext_byte = ct_data[msg_idx][pos]
            keystream[pos] = ciphertext_byte ^ plaintext_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = bytearray()
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We know the keystream at this position
            plaintext_byte = ct_data[target_msg_idx][pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # We don't have keystream for this position
            # This shouldn't happen if the problem is solvable
            result.append(0)
    
    output = {
        "plaintext": result.hex()
    }
    print(json.dumps(output))

if __name__ == '__main__':
    main()
