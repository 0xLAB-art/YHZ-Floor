import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': hex_to_bytes(ct['data']),
            'message_index': ct['message_index']
        })
    
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        known_plaintexts.append({
            'data': hex_to_bytes(kp['data']),
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get target ciphertext
    target_ct = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ct = ct['data']
            break
    
    # Recover keystream for positions target_offset to target_offset + target_length
    keystream = bytearray(target_length)
    
    for i in range(target_length):
        pos = target_offset + i
        
        # Find a known plaintext that covers this position
        for kp in known_plaintexts:
            kp_start = kp['offset']
            kp_end = kp['offset'] + len(kp['data'])
            
            if kp_start <= pos < kp_end:
                # This known plaintext covers position pos
                kp_msg_idx = kp['message_index']
                
                # Get the ciphertext for this message
                kp_ct = None
                for ct in ciphertexts:
                    if ct['message_index'] == kp_msg_idx:
                        kp_ct = ct['data']
                        break
                
                # Calculate keystream: keystream[pos] = plaintext[pos] XOR ciphertext[pos]
                plaintext_byte = kp['data'][pos - kp_start]
                ciphertext_byte = kp_ct[pos]
                keystream[i] = plaintext_byte ^ ciphertext_byte
                break
    
    # Decrypt target using recovered keystream
    plaintext = bytearray(target_length)
    for i in range(target_length):
        plaintext[i] = target_ct[target_offset + i] ^ keystream[i]
    
    result = {
        'plaintext': bytes_to_hex(bytes(plaintext))
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()