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
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(hex_to_bytes(ct['data']))
    
    # Recover keystream from known plaintexts
    # keystream[message_index][offset] = plaintext XOR ciphertext
    max_length = max(len(ct) for ct in ct_bytes)
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = hex_to_bytes(kp['data'])
        
        if msg_idx not in keystream:
            keystream[msg_idx] = {}
        
        # Extract the corresponding ciphertext bytes
        ct_segment = ct_bytes[msg_idx][offset:offset + len(pt_data)]
        
        # Recover keystream: keystream = plaintext XOR ciphertext
        ks_segment = xor_bytes(pt_data, ct_segment)
        
        # Store keystream bytes
        for i, ks_byte in enumerate(ks_segment):
            keystream[msg_idx][offset + i] = ks_byte
    
    # Extract target ciphertext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx][target_offset:target_offset + target_length]
    
    # Decrypt target using recovered keystream
    # Assuming the same keystream is used across messages (many-time pad)
    # Try to find keystream from any message at the required positions
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        ks_byte = None
        
        # Try to find keystream at this position from any message
        for msg_idx in keystream:
            if pos in keystream[msg_idx]:
                ks_byte = keystream[msg_idx][pos]
                break
        
        if ks_byte is not None:
            # Decrypt: plaintext = ciphertext XOR keystream
            pt_byte = target_ct[i] ^ ks_byte
            plaintext.append(pt_byte)
        else:
            # No keystream available at this position - this shouldn't happen
            # if the problem is solvable, but handle it anyway
            plaintext.append(0)
    
    result = {
        "plaintext": bytes_to_hex(bytes(plaintext))
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
