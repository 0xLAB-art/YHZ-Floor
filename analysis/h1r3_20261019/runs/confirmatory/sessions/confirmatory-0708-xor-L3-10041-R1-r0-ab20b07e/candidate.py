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
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Find max length to know keystream size needed
    max_len = max(len(ct) for ct in ct_map.values())
    
    # Recover keystream
    keystream = [None] * max_len
    
    # For each known plaintext, recover keystream bytes
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = hex_to_bytes(kp['data'])
        ct_bytes = ct_map[msg_idx]
        
        for i, pt_byte in enumerate(pt_bytes):
            pos = offset + i
            if pos < len(ct_bytes):
                # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
                ks_byte = ct_bytes[pos] ^ pt_byte
                if keystream[pos] is None:
                    keystream[pos] = ks_byte
                elif keystream[pos] != ks_byte:
                    # Consistency check - should not happen with valid data
                    pass
    
    # Now decrypt the target message
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_map[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have keystream, we need to try other methods
            # For now, we'll use 0x00 as placeholder (this shouldn't happen with good data)
            plaintext_bytes.append(0)
    
    result = {
        "plaintext": bytes(plaintext_bytes).hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
