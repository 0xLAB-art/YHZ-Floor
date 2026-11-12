import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(b1, b2):
    return bytes(a ^ b for a, b in zip(b1, b2))

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        ct_data[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = hex_to_bytes(kp['data'])
        
        # Get corresponding ciphertext bytes
        ct_bytes = ct_data[msg_idx][offset:offset+len(pt_bytes)]
        
        # Recover keystream: key = plaintext XOR ciphertext
        key_bytes = xor_bytes(pt_bytes, ct_bytes)
        
        # Store each keystream byte
        for i, key_byte in enumerate(key_bytes):
            pos = offset + i
            if pos in keystream:
                # Verify consistency
                if keystream[pos] != key_byte:
                    raise ValueError(f"Inconsistent keystream at position {pos}")
            else:
                keystream[pos] = key_byte
    
    # Decrypt target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_data[target_msg_idx][target_offset:target_offset+target_length]
    
    # Decrypt using recovered keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos not in keystream:
            raise ValueError(f"Missing keystream at position {pos}")
        
        pt_byte = target_ct[i] ^ keystream[pos]
        plaintext_bytes.append(pt_byte)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
