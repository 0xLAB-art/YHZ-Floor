import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ct_dict = {}
    for ct in ciphertexts:
        msg_idx = ct['message_index']
        ct_dict[msg_idx] = hex_to_bytes(ct['data'])
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = hex_to_bytes(kp['data'])
        
        # Get corresponding ciphertext bytes
        ct_bytes = ct_dict[msg_idx][offset:offset + len(pt_bytes)]
        
        # Recover keystream: K = P ⊕ C
        for i, (p, c) in enumerate(zip(pt_bytes, ct_bytes)):
            keystream[offset + i] = p ^ c
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_dict[target_msg_idx]
    plaintext_bytes = bytearray()
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: P = C ⊕ K
            ct_byte = target_ct[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # This shouldn't happen if we have enough known plaintexts
            # But as fallback, we could try other techniques
            plaintext_bytes.append(0)
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(plaintext_bytes)
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()
