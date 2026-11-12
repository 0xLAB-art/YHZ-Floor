import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        ct_data[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build known plaintext map: (message_index, offset) -> byte_value
    known_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        for i, byte_val in enumerate(data):
            known_map[(msg_idx, offset + i)] = byte_val
    
    # For stream cipher (likely XOR with keystream), we can recover keystream bytes
    # If C = P XOR K, then K = P XOR C
    keystream = {}
    for (msg_idx, offset), plaintext_byte in known_map.items():
        if msg_idx in ct_data and offset < len(ct_data[msg_idx]):
            ciphertext_byte = ct_data[msg_idx][offset]
            keystream[offset] = plaintext_byte ^ ciphertext_byte
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_data:
        result = {'plaintext': '00' * target_length}
    else:
        target_ct = ct_data[target_msg_idx]
        plaintext_bytes = []
        
        for i in range(target_length):
            pos = target_offset + i
            if pos in keystream and pos < len(target_ct):
                # Decrypt: P = C XOR K
                plaintext_byte = target_ct[pos] ^ keystream[pos]
                plaintext_bytes.append(plaintext_byte)
            else:
                # Unknown - use 0x00 as placeholder
                plaintext_bytes.append(0)
        
        plaintext_hex = bytes(plaintext_bytes).hex()
        result = {'plaintext': plaintext_hex}
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
