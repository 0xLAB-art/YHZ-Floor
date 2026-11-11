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
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_bytes = hex_to_bytes(kp['data'])
        
        if msg_idx in ct_map:
            ct_bytes = ct_map[msg_idx]
            
            # Recover keystream: keystream = plaintext XOR ciphertext
            for i, pt_byte in enumerate(pt_bytes):
                pos = offset + i
                if pos < len(ct_bytes):
                    ks_byte = pt_byte ^ ct_bytes[pos]
                    keystream[pos] = ks_byte
    
    # Now decrypt the target message using recovered keystream
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
            # If we don't have keystream for this position, try to derive it
            # from other messages with known plaintext
            plaintext.append(0)
    
    result = {"plaintext": bytes_to_hex(bytes(plaintext))}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
