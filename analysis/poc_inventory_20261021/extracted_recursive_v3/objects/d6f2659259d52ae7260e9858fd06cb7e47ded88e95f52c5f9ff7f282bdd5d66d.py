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
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = hex_to_bytes(ct['data'])
    
    known = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = hex_to_bytes(kp['data'])
        if msg_idx not in known:
            known[msg_idx] = {}
        for i, byte in enumerate(data):
            known[msg_idx][offset + i] = byte
    
    # Recover keystream from known plaintexts
    keystream = {}
    for msg_idx, plaintext_map in known.items():
        if msg_idx in ciphertexts:
            ct = ciphertexts[msg_idx]
            for pos, pt_byte in plaintext_map.items():
                if pos < len(ct):
                    keystream[pos] = ct[pos] ^ pt_byte
    
    # Decrypt target message
    target_ct = ciphertexts[target_msg_idx]
    plaintext = bytearray(target_length)
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            plaintext[i] = target_ct[pos] ^ keystream[pos]
        else:
            plaintext[i] = 0
    
    result = {
        "plaintext": bytes_to_hex(bytes(plaintext))
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()