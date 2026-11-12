import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        ciphertexts[idx] = bytes.fromhex(ct['data'])
    
    known = {}
    for kp in instance['known_plaintexts']:
        idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if idx not in known:
            known[idx] = {}
        for i, b in enumerate(data):
            known[idx][offset + i] = b
    
    target_msg = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    keystream = {}
    for msg_idx in known:
        for pos, plaintext_byte in known[msg_idx].items():
            if pos < len(ciphertexts[msg_idx]):
                key_byte = ciphertexts[msg_idx][pos] ^ plaintext_byte
                keystream[pos] = key_byte
    
    result = []
    for i in range(target_offset, target_offset + target_length):
        if i in keystream and i < len(ciphertexts[target_msg]):
            plaintext_byte = ciphertexts[target_msg][i] ^ keystream[i]
            result.append(plaintext_byte)
        else:
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == '__main__':
    main()
