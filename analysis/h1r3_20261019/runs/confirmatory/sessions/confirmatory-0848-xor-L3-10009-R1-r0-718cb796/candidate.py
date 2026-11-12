import json
import sys

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    cipher_data = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        cipher_data[msg_idx] = hex_to_bytes(ct['data'])
    
    # Recover keystream from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        # Get corresponding ciphertext bytes
        ciphertext_bytes = cipher_data[msg_idx][offset:offset + len(plaintext_bytes)]
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, (p, c) in enumerate(zip(plaintext_bytes, ciphertext_bytes)):
            pos = offset + i
            key_byte = p ^ c
            keystream[pos] = key_byte
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = cipher_data[target_msg_idx][target_offset:target_offset + target_length]
    
    plaintext_bytes = bytearray()
    for i, c in enumerate(target_ciphertext):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: plaintext = ciphertext XOR keystream
            p = c ^ keystream[pos]
            plaintext_bytes.append(p)
        else:
            # If keystream byte is unknown, we cannot decrypt this byte
            # This shouldn't happen if we have enough known plaintexts
            plaintext_bytes.append(0)
    
    result = {
        "plaintext": bytes_to_hex(plaintext_bytes)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
