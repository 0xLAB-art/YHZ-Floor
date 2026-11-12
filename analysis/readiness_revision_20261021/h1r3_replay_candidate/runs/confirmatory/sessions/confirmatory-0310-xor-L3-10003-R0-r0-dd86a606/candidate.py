import json
import sys

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(data):
    return data.hex()

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert ciphertexts to bytes
    ct_data = []
    for ct in ciphertexts:
        ct_data.append(hex_to_bytes(ct['data']))
    
    # Recover keystream from known plaintexts
    # keystream[offset] = plaintext[offset] XOR ciphertext[offset]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = hex_to_bytes(kp['data'])
        
        for i, pt_byte in enumerate(pt_bytes):
            pos = offset + i
            ct_byte = ct_data[msg_idx][pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt using known keystream
            ct_byte = ct_data[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            # But handle it gracefully
            plaintext_bytes.append(0)
    
    result = {
        "plaintext": bytes(plaintext_bytes).hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
