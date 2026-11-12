import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a dictionary of ciphertexts by message_index
    cipher_dict = {}
    for ct in ciphertexts:
        cipher_dict[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream from known plaintexts
    # keystream[position] = known byte value
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_data = hex_to_bytes(kp['data'])
        
        if msg_idx in cipher_dict:
            ciphertext = cipher_dict[msg_idx]
            
            # For each byte in this known plaintext
            for i, pt_byte in enumerate(plaintext_data):
                pos = offset + i
                if pos < len(ciphertext):
                    ct_byte = ciphertext[pos]
                    # keystream[pos] = plaintext XOR ciphertext
                    keystream[pos] = pt_byte ^ ct_byte
    
    # Now decrypt the target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in cipher_dict:
        # Can't decrypt without ciphertext
        result = {"plaintext": "00" * target_length}
        print(json.dumps(result))
        return
    
    target_ciphertext = cipher_dict[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Unknown keystream position - shouldn't happen with enough known plaintexts
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes_to_hex(bytes(plaintext_bytes))
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()