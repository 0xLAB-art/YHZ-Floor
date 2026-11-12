import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Parse ciphertexts into byte arrays
    ct_dict = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_dict[msg_idx] = bytes.fromhex(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = bytes.fromhex(kp['data'])
        
        if msg_idx in ct_dict:
            ct_bytes = ct_dict[msg_idx]
            for i, pt_byte in enumerate(pt_bytes):
                pos = offset + i
                if pos < len(ct_bytes):
                    # K[pos] = P[pos] XOR C[pos]
                    keystream[pos] = pt_byte ^ ct_bytes[pos]
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_dict:
        result = {"plaintext": "00" * target_length}
    else:
        target_ct = ct_dict[target_msg_idx]
        plaintext_bytes = []
        
        for i in range(target_length):
            pos = target_offset + i
            if pos in keystream and pos < len(target_ct):
                # P[pos] = C[pos] XOR K[pos]
                pt_byte = target_ct[pos] ^ keystream[pos]
                plaintext_bytes.append(pt_byte)
            else:
                # No keystream recovered for this position
                plaintext_bytes.append(0)
        
        plaintext_hex = bytes(plaintext_bytes).hex()
        result = {"plaintext": plaintext_hex}
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()