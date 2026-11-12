import sys
import json

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert all ciphertexts to bytes
    ciphertext_data = []
    for ct in ciphertexts:
        ciphertext_data.append(hex_to_bytes(ct['data']))
    
    # Recover keystream from known plaintexts
    # keystream[position] = plaintext XOR ciphertext
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = hex_to_bytes(kp['data'])
        
        ciphertext = ciphertext_data[msg_idx]
        
        # Recover keystream at this position
        for i, pt_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                ct_byte = ciphertext[pos]
                keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_data[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt it
            # This shouldn't happen with a well-formed instance
            plaintext_bytes.append(0)
    
    result = {
        "plaintext": bytes(plaintext_bytes).hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()