import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert ciphertexts to bytes
    cipher_data = {}
    for ct in ciphertexts:
        cipher_data[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Determine the maximum length we might need
    max_len = max(len(c) for c in cipher_data.values())
    
    # Recover keystream: for each position, use known plaintexts to find the key
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        ciphertext = cipher_data[msg_idx]
        
        # Recover keystream at these positions: K = P XOR C
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                c_byte = ciphertext[pos]
                k_byte = p_byte ^ c_byte
                
                # Verify consistency if we already have this keystream byte
                if keystream[pos] is not None:
                    if keystream[pos] != k_byte:
                        # Inconsistency - shouldn't happen with valid input
                        pass
                else:
                    keystream[pos] = k_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = cipher_data[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # If we don't have the keystream, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext_bytes.append(0)
    
    result = {
        "plaintext": bytes(plaintext_bytes).hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
