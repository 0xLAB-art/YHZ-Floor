import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build known plaintext map: (message_index, offset) -> plaintext_byte
    known_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        for i, byte in enumerate(data):
            known_map[(msg_idx, offset + i)] = byte
    
    # This is a stream cipher reuse attack (same keystream for all messages)
    # If C_i = P_i XOR K, then C_i XOR P_i = K
    # Once we know K at position j, we can decrypt any ciphertext at position j
    
    # Recover keystream from known plaintexts
    keystream = {}
    for (msg_idx, pos), plaintext_byte in known_map.items():
        if msg_idx in ct_bytes and pos < len(ct_bytes[msg_idx]):
            ciphertext_byte = ct_bytes[msg_idx][pos]
            keystream[pos] = ciphertext_byte ^ plaintext_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and target_msg_idx in ct_bytes and pos < len(ct_bytes[target_msg_idx]):
            ciphertext_byte = ct_bytes[target_msg_idx][pos]
            plaintext_byte = ciphertext_byte ^ keystream[pos]
            plaintext.append(plaintext_byte)
        else:
            # If keystream not known at this position, we can't decrypt
            # This shouldn't happen if the instance is solvable
            plaintext.append(0)
    
    # Convert to hex string
    plaintext_hex = bytes(plaintext).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()