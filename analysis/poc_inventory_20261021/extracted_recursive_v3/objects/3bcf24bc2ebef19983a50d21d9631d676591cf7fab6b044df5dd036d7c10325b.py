import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # Recover keystream from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = bytes.fromhex(kp['data'])
        
        for i in range(len(plaintext)):
            pos = offset + i
            p_byte = plaintext[i]
            c_byte = ct_bytes[msg_idx][pos]
            k_byte = p_byte ^ c_byte
            keystream[pos] = k_byte
    
    # Decrypt the target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        c_byte = ct_bytes[target_msg_idx][pos]
        k_byte = keystream[pos]
        p_byte = c_byte ^ k_byte
        plaintext.append(p_byte)
    
    result = {"plaintext": bytes(plaintext).hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()