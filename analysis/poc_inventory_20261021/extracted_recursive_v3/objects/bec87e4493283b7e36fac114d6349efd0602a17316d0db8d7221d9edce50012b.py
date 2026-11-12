import sys
import json

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(data):
    return data.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

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
    
    # Build known plaintext map
    pt_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = hex_to_bytes(kp['data'])
        if msg_idx not in pt_map:
            pt_map[msg_idx] = {}
        for i, byte in enumerate(data):
            pt_map[msg_idx][offset + i] = byte
    
    # Recover keystream bytes from known plaintexts
    # keystream[pos] = plaintext[pos] ^ ciphertext[pos]
    keystream = {}
    for msg_idx, positions in pt_map.items():
        if msg_idx in ct_map:
            ct = ct_map[msg_idx]
            for pos, pt_byte in positions.items():
                if pos < len(ct):
                    keystream[pos] = pt_byte ^ ct[pos]
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_map:
        result = {"plaintext": "00" * target_length}
        print(json.dumps(result))
        return
    
    target_ct = ct_map[target_msg_idx]
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Unknown byte - use 0x00 as fallback
            plaintext.append(0x00)
    
    result = {"plaintext": bytes_to_hex(bytes(plaintext))}
    print(json.dumps(result))

if __name__ == '__main__':
    main()