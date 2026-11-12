import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert hex ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_data[msg_idx] = bytes.fromhex(ct['data'])
    
    # Length of messages
    msg_len = len(ct_data[0])
    
    # Recover keystream using known plaintexts
    keystream = [None] * msg_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        # Recover keystream: K = P ⊕ C
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            c_byte = ct_data[msg_idx][pos]
            k_byte = p_byte ^ c_byte
            keystream[pos] = k_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if keystream[pos] is not None:
            # We have the keystream byte, decrypt directly
            c_byte = ct_data[target_msg_idx][pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext.append(p_byte)
        else:
            # Try to recover keystream from other messages
            # Find a message with known plaintext at this position
            found = False
            for kp in known_plaintexts:
                kp_msg_idx = kp['message_index']
                kp_offset = kp['offset']
                kp_data = bytes.fromhex(kp['data'])
                
                if kp_offset <= pos < kp_offset + len(kp_data):
                    # This known plaintext covers position pos
                    kp_byte = kp_data[pos - kp_offset]
                    c_byte = ct_data[kp_msg_idx][pos]
                    k_byte = kp_byte ^ c_byte
                    keystream[pos] = k_byte
                    
                    # Now decrypt target
                    target_c_byte = ct_data[target_msg_idx][pos]
                    p_byte = target_c_byte ^ k_byte
                    plaintext.append(p_byte)
                    found = True
                    break
            
            if not found:
                # This shouldn't happen if the problem is well-formed
                plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
