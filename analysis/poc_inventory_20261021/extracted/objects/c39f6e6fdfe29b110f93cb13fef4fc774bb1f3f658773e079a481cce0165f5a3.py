import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # XOR property: C_i = P_i XOR K, so C_i XOR C_j = P_i XOR P_j
    # If we know P_i at position pos, we can find K at that position: K[pos] = C_i[pos] XOR P_i[pos]
    # Then we can decrypt any other ciphertext at that position: P_j[pos] = C_j[pos] XOR K[pos]
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Reconstruct the keystream from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_hex = kp['data']
        pt_bytes = bytes.fromhex(pt_hex)
        
        ct = ct_bytes[msg_idx]
        
        for i, pt_byte in enumerate(pt_bytes):
            pos = offset + i
            # K[pos] = C[pos] XOR P[pos]
            key_byte = ct[pos] ^ pt_byte
            keystream[pos] = key_byte
    
    # Decrypt the target message using the recovered keystream
    target_ct = ct_bytes[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # P[pos] = C[pos] XOR K[pos]
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
