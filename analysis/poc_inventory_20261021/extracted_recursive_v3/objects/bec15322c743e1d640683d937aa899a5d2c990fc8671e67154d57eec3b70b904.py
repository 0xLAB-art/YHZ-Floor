import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ct_dict = {}
    for ct in ciphertexts:
        ct_dict[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Recover keystream
    target_start = target['offset']
    target_end = target['offset'] + target['length']
    
    keystream = [None] * 256  # Assume max position is reasonable
    
    # For each known plaintext, recover the keystream
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        if msg_idx not in ct_dict:
            continue
            
        ct = ct_dict[msg_idx]
        
        # XOR plaintext with ciphertext to get keystream
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(keystream):
                ct_byte = ct[pos]
                keystream[pos] = pt_byte ^ ct_byte
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_ct = ct_dict[target_msg_idx]
    
    plaintext_bytes = bytearray(target['length'])
    
    for i in range(target['length']):
        pos = target_start + i
        if pos < len(keystream) and keystream[pos] is not None:
            plaintext_bytes[i] = target_ct[pos] ^ keystream[pos]
        else:
            plaintext_bytes[i] = 0
    
    result = {"plaintext": plaintext_bytes.hex()}
    print(json.dumps(result))

if __name__ == "__main__":
    main()