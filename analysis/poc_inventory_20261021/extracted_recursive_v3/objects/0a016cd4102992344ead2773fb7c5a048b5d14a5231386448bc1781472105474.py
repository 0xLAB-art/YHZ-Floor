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
    ct_map = {}
    max_len = 0
    for ct in ciphertexts:
        idx = ct['message_index']
        data = hex_to_bytes(ct['data'])
        ct_map[idx] = data
        max_len = max(max_len, len(data))
    
    # Recover keystream from known plaintexts
    # keystream[position] = ciphertext[position] XOR plaintext[position]
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        if msg_idx not in ct_map:
            continue
            
        ciphertext = ct_map[msg_idx]
        
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                ct_byte = ciphertext[pos]
                ks_byte = ct_byte ^ pt_byte
                
                # Store keystream byte (verify consistency if already set)
                if keystream[pos] is None:
                    keystream[pos] = ks_byte
                elif keystream[pos] != ks_byte:
                    # Inconsistency - should not happen with correct input
                    pass
    
    # Now decrypt the target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_map:
        print(json.dumps({"plaintext": "00" * target_length}))
        return
    
    target_ciphertext = ct_map[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and pos < len(keystream) and keystream[pos] is not None:
            ct_byte = target_ciphertext[pos]
            ks_byte = keystream[pos]
            pt_byte = ct_byte ^ ks_byte
            plaintext_bytes.append(pt_byte)
        else:
            # No keystream recovered for this position
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()