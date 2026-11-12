import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        msg_idx = ct['message_index']
        data = bytes.fromhex(ct['data'])
        ciphertexts[msg_idx] = data
    
    target_ciphertext = ciphertexts[target_msg_idx]
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_data = bytes.fromhex(kp['data'])
        
        if msg_idx in ciphertexts:
            ciphertext = ciphertexts[msg_idx]
            for i, p_byte in enumerate(plaintext_data):
                pos = offset + i
                if pos < len(ciphertext):
                    k_byte = ciphertext[pos] ^ p_byte
                    keystream[pos] = k_byte
    
    # Decrypt target using recovered keystream
    result = bytearray()
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            result.append(p_byte)
        else:
            # Should not happen if we have enough known plaintexts
            result.append(0)
    
    output = {
        "plaintext": result.hex()
    }
    print(json.dumps(output))

if __name__ == '__main__':
    main()
