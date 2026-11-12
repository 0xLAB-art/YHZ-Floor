import json
import sys

def hex_to_bytes(h):
    return bytes.fromhex(h)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream from known plaintexts
    # keystream[pos] = plaintext[pos] XOR ciphertext[pos]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = hex_to_bytes(kp['data'])
        
        ct = ct_map[msg_idx]
        
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(ct):
                ks_byte = pt_byte ^ ct[pos]
                keystream[pos] = ks_byte
    
    # Decrypt target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_map[target_msg_idx]
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # If keystream not known at this position, we can't decrypt
            # Try to use cribbing or other techniques, but for now use 0
            plaintext.append(0)
    
    result = {
        "plaintext": bytes_to_hex(bytes(plaintext))
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
