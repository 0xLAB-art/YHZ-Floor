import json
import sys

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes and index by message_index
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream bytes using known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = hex_to_bytes(kp['data'])
        
        if msg_idx not in ct_map:
            continue
            
        ct_data = ct_map[msg_idx]
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(ct_data):
                ks_byte = pt_byte ^ ct_data[pos]
                keystream[pos] = ks_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_map:
        print(json.dumps({"plaintext": "00" * target_length}))
        return
    
    target_ct = ct_map[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            # Decrypt: plaintext = ciphertext XOR keystream
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # No keystream available for this position
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes_to_hex(bytes(plaintext_bytes))
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
