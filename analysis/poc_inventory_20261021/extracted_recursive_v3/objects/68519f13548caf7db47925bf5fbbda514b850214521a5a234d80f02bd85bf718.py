import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Convert ciphertexts to bytes
    ct_bytes = {}
    for ct in ciphertexts:
        ct_bytes[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build known plaintext map
    known = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in known:
            known[msg_idx] = {}
        for i, byte in enumerate(data):
            known[msg_idx][offset + i] = byte
    
    # Recover keystream from known plaintexts
    keystream = {}
    for msg_idx in known:
        if msg_idx in ct_bytes:
            for pos, pt_byte in known[msg_idx].items():
                ct_byte = ct_bytes[msg_idx][pos]
                keystream[pos] = ct_byte ^ pt_byte
    
    # Decrypt target message using recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    if target_msg_idx not in ct_bytes:
        result = {"plaintext": "00" * target_length}
        print(json.dumps(result))
        return
    
    target_ct = ct_bytes[target_msg_idx]
    plaintext = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            plaintext.append(0)
    
    plaintext_hex = bytes(plaintext).hex()
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
