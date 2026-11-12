import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        ct_data[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = hex_to_bytes(kp['data'])
        
        # Get the corresponding ciphertext bytes
        ct_bytes = ct_data[msg_idx][offset:offset + len(pt_bytes)]
        
        # Recover keystream: K = P ⊕ C
        ks_bytes = xor_bytes(pt_bytes, ct_bytes)
        
        # Store keystream bytes
        for i, b in enumerate(ks_bytes):
            keystream[offset + i] = b
    
    # Decrypt target using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_data[target_msg_idx][target_offset:target_offset + target_length]
    
    # Decrypt using keystream
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            plaintext.append(target_ct[i] ^ keystream[pos])
        else:
            # If we don't have keystream at this position, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext.append(0)
    
    plaintext_bytes = bytes(plaintext)
    result = {"plaintext": bytes_to_hex(plaintext_bytes)}
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()