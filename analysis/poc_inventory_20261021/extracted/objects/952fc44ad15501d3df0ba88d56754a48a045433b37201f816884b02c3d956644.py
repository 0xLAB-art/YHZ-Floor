import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    cipher_bytes = []
    for ct in ciphertexts:
        cipher_bytes.append(bytes.fromhex(ct['data']))
    
    # Recover keystream from known plaintexts
    # We need keystream for positions target_offset to target_offset + target_length
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Initialize keystream as None for unknown positions
    max_len = max(len(cb) for cb in cipher_bytes)
    keystream = [None] * max_len
    
    # Extract keystream from known plaintexts
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_hex = kp['data']
        plaintext_bytes = bytes.fromhex(plaintext_hex)
        
        # Recover keystream: K = P XOR C
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            c_byte = cipher_bytes[msg_idx][pos]
            k_byte = p_byte ^ c_byte
            keystream[pos] = k_byte
    
    # Decrypt target using recovered keystream
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if keystream[pos] is not None:
            c_byte = cipher_bytes[target_msg_idx][pos]
            p_byte = c_byte ^ keystream[pos]
            result.append(p_byte)
        else:
            # Should not happen if we have enough known plaintexts
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    
    output = {
        "plaintext": plaintext_hex
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
