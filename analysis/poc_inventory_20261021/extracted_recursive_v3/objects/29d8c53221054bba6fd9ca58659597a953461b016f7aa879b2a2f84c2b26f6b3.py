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
        ct_dict[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Recover keystream
    # Initialize keystream array for the range we need
    target_start = target['offset']
    target_end = target['offset'] + target['length']
    
    keystream = {}
    
    # For each known plaintext, recover the keystream
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = hex_to_bytes(kp['data'])
        
        if msg_idx not in ct_dict:
            continue
            
        ct = ct_dict[msg_idx]
        
        # XOR plaintext with ciphertext to get keystream
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if target_start <= pos < target_end:
                ct_byte = ct[pos]
                keystream[pos] = pt_byte ^ ct_byte
    
    # Now decrypt the target message using recovered keystream
    target_msg_idx = target['message_index']
    target_ct = ct_dict[target_msg_idx]
    
    plaintext_bytes = bytearray(target['length'])
    
    for i in range(target['length']):
        pos = target_start + i
        if pos in keystream:
            plaintext_bytes[i] = target_ct[pos] ^ keystream[pos]
        else:
            # If we don't have the keystream at this position, we can't decrypt
            # This shouldn't happen if we have enough known plaintexts
            plaintext_bytes[i] = 0
    
    result = {
        "plaintext": bytes_to_hex(plaintext_bytes)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()