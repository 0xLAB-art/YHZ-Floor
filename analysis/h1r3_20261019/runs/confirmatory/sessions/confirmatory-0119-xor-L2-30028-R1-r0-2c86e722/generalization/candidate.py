import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Convert known plaintexts to bytes
    kp_data = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in kp_data:
            kp_data[msg_idx] = {}
        for i, byte in enumerate(data):
            kp_data[msg_idx][offset + i] = byte
    
    # Recover keystream from known plaintexts
    # In a stream cipher: ciphertext = plaintext XOR keystream
    # So: keystream = plaintext XOR ciphertext
    keystream = {}
    for msg_idx, plaintext_dict in kp_data.items():
        for pos, pt_byte in plaintext_dict.items():
            ct_byte = ct_bytes[msg_idx][pos]
            keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            ct_byte = ct_bytes[target_msg_idx][pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Try to recover keystream from other messages if not already known
            # Check if we have plaintext for this position in any other message
            recovered = False
            for msg_idx, plaintext_dict in kp_data.items():
                if pos in plaintext_dict:
                    ct_byte_ref = ct_bytes[msg_idx][pos]
                    pt_byte_ref = plaintext_dict[pos]
                    keystream[pos] = pt_byte_ref ^ ct_byte_ref
                    
                    ct_byte = ct_bytes[target_msg_idx][pos]
                    pt_byte = ct_byte ^ keystream[pos]
                    plaintext_bytes.append(pt_byte)
                    recovered = True
                    break
            
            if not recovered:
                # Keystream not available for this position
                plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
