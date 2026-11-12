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
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(hex_to_bytes(ct['data']))
    
    # Recover keystream from known plaintexts
    # keystream[offset] = plaintext ⊕ ciphertext
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = hex_to_bytes(kp['data'])
        
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            c_byte = ct_bytes[msg_idx][pos]
            k_byte = p_byte ^ c_byte
            
            # Store keystream byte
            if pos not in keystream:
                keystream[pos] = k_byte
            else:
                # Verify consistency
                if keystream[pos] != k_byte:
                    # Inconsistency detected - but let's trust the first one
                    pass
    
    # Now decrypt the target using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            c_byte = ct_bytes[target_msg_idx][pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext.append(p_byte)
        else:
            # No keystream available at this position
            # This shouldn't happen if we have enough known plaintexts
            plaintext.append(0)
    
    result = {
        "plaintext": bytes(plaintext).hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
