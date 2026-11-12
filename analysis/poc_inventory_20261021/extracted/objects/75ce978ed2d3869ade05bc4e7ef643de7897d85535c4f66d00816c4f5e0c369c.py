import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ciphertext_data = {}
    for ct in ciphertexts:
        ciphertext_data[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Convert known plaintexts to bytes
    known_data = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known_data:
            known_data[msg_idx] = {}
        for i, byte in enumerate(data):
            known_data[msg_idx][offset + i] = byte
    
    # For stream cipher reuse attack:
    # C_i = P_i XOR K
    # C_j = P_j XOR K
    # Therefore: C_i XOR C_j = P_i XOR P_j
    # If we know P_i, we can recover P_j: P_j = P_i XOR C_i XOR C_j
    
    # Recover keystream from known plaintexts
    keystream = {}
    for msg_idx in known_data:
        if msg_idx in ciphertext_data:
            for offset, plaintext_byte in known_data[msg_idx].items():
                if offset < len(ciphertext_data[msg_idx]):
                    # K[offset] = P[offset] XOR C[offset]
                    keystream[offset] = plaintext_byte ^ ciphertext_data[msg_idx][offset]
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_data[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            # P = C XOR K
            plaintext_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(plaintext_byte)
        else:
            # Can't decrypt this byte - shouldn't happen if we have enough known plaintext
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {
        "plaintext": plaintext_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
