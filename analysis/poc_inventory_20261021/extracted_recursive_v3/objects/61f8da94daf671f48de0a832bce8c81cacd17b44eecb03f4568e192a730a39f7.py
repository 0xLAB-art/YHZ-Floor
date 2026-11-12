import json
import sys

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
    
    # This is a stream cipher reuse attack (many-time pad)
    # When the same keystream is used for multiple messages:
    # C_i = P_i XOR K
    # C_j = P_j XOR K
    # Therefore: C_i XOR C_j = P_i XOR P_j
    # And if we know P_i, we can recover K at that position: K = C_i XOR P_i
    
    # Recover the keystream at known positions
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_hex = kp['data']
        plaintext_bytes = bytes.fromhex(plaintext_hex)
        
        # Recover keystream: K = C XOR P
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            c_byte = ct_bytes[msg_idx][pos]
            k_byte = c_byte ^ p_byte
            keystream[pos] = k_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: P = C XOR K
            c_byte = ct_bytes[target_msg_idx][pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have the keystream at this position, we can't decrypt
            # This shouldn't happen if the instance is solvable
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()