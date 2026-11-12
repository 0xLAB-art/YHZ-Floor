import sys
import json

def hex_to_bytes(h):
    return bytes.fromhex(h)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Parse ciphertexts into bytes
    ct_dict = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_dict[msg_idx] = hex_to_bytes(ct['data'])
    
    # Recover keystream from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = hex_to_bytes(kp['data'])
        
        ct_data = ct_dict[msg_idx]
        
        # For each byte in this known plaintext
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            ct_byte = ct_data[pos]
            # keystream[pos] = plaintext[pos] XOR ciphertext[pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_dict[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: plaintext = ciphertext XOR keystream
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # No keystream byte available - this shouldn't happen if problem is solvable
            # Try to make educated guess or fail gracefully
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes_to_hex(bytes(plaintext_bytes))
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()