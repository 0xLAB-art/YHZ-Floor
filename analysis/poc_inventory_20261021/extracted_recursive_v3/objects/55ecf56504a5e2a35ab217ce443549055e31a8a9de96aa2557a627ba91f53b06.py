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
    ct_dict = {}
    for ct in ciphertexts:
        ct_dict[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        if msg_idx in ct_dict:
            ciphertext = ct_dict[msg_idx]
            for i, pt_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
                    keystream[pos] = ciphertext[pos] ^ pt_byte
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_dict:
        # Should not happen based on problem structure
        result = {"plaintext": "00" * target_length}
    else:
        target_ciphertext = ct_dict[target_msg_idx]
        plaintext_bytes = []
        
        for i in range(target_length):
            pos = target_offset + i
            if pos in keystream and pos < len(target_ciphertext):
                # plaintext[pos] = ciphertext[pos] XOR keystream[pos]
                pt_byte = target_ciphertext[pos] ^ keystream[pos]
                plaintext_bytes.append(pt_byte)
            else:
                # Missing keystream byte - should not happen if problem is solvable
                plaintext_bytes.append(0)
        
        result = {"plaintext": bytes_to_hex(bytes(plaintext_bytes))}
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
