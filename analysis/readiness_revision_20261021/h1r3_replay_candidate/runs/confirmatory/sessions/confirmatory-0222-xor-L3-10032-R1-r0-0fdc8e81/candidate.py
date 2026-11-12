import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ct_data = {}
    for ct in ciphertexts:
        ct_data[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = hex_to_bytes(kp['data'])
        
        if msg_idx in ct_data:
            ciphertext = ct_data[msg_idx]
            
            # Recover keystream: K = P ⊕ C
            for i, p_byte in enumerate(plaintext):
                pos = offset + i
                if pos < len(ciphertext):
                    k_byte = p_byte ^ ciphertext[pos]
                    keystream[pos] = k_byte
    
    # Now decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_data:
        print(json.dumps({"plaintext": "00" * target_length}))
        return
    
    target_ct = ct_data[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        
        if pos in keystream and pos < len(target_ct):
            # Decrypt: P = C ⊕ K
            p_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # No keystream available for this position
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes_to_hex(bytes(plaintext_bytes))
    
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()
