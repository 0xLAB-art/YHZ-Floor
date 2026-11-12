import sys
import json

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
    
    # Build a dictionary of ciphertext data by message_index
    ct_dict = {}
    for ct in ciphertexts:
        ct_dict[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    # keystream[position] = plaintext[position] XOR ciphertext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = hex_to_bytes(kp['data'])
        
        if msg_idx in ct_dict:
            ct_data = ct_dict[msg_idx]
            for i, pt_byte in enumerate(pt_data):
                pos = offset + i
                if pos < len(ct_data):
                    ks_byte = pt_byte ^ ct_data[pos]
                    keystream[pos] = ks_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_dict:
        print(json.dumps({"plaintext": "00" * target_length}))
        return
    
    target_ct = ct_dict[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == '__main__':
    main()