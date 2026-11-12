import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ciphertext_bytes = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ciphertext_bytes[msg_idx] = bytes.fromhex(ct['data'])
    
    # Recover keystream from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_data = bytes.fromhex(kp['data'])
        
        if msg_idx in ciphertext_bytes:
            ciphertext = ciphertext_bytes[msg_idx]
            for i, pt_byte in enumerate(plaintext_data):
                pos = offset + i
                if pos < len(ciphertext):
                    keystream[pos] = ciphertext[pos] ^ pt_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ciphertext_bytes:
        result = {"plaintext": "00" * target_length}
        print(json.dumps(result))
        return
    
    target_ciphertext = ciphertext_bytes[target_msg_idx]
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Unknown keystream position - cannot decrypt
            plaintext.append(0)
    
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext)
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()