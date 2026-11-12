import sys
import json

def hex_to_bytes(h):
    return bytes.fromhex(h)

def bytes_to_hex(b):
    return b.hex()

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a mapping from message_index to ciphertext bytes
    ct_map = {}
    for ct_obj in ciphertexts:
        ct_map[ct_obj['message_index']] = hex_to_bytes(ct_obj['data'])
    
    # Recover keystream bytes from known plaintexts
    # keystream[position] = ciphertext[position] XOR plaintext[position]
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = hex_to_bytes(kp['data'])
        
        if msg_idx in ct_map:
            ct = ct_map[msg_idx]
            for i, pt_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ct):
                    keystream[pos] = ct[pos] ^ pt_byte
    
    # Decrypt the target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_map:
        result = {"plaintext": "00" * target_length}
        print(json.dumps(result))
        return
    
    target_ct = ct_map[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If keystream not known at this position, we can't decrypt
            plaintext_bytes.append(0)
    
    result = {"plaintext": bytes_to_hex(bytes(plaintext_bytes))}
    print(json.dumps(result))

if __name__ == "__main__":
    main()