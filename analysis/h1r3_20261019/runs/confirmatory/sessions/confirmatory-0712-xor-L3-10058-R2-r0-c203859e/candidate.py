import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        plaintext = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': plaintext,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target_length = instance['target']['length']
    target_message_index = instance['target']['message_index']
    target_offset = instance['target']['offset']
    
    keystream = [None] * 300
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext is None:
            continue
        
        for i, pb in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                key_byte = ciphertext[pos] ^ pb
                if keystream[pos] is None:
                    keystream[pos] = key_byte
                elif keystream[pos] != key_byte:
                    pass
    
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_message_index:
            target_ciphertext = ct['data']
            break
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            plaintext_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext.append(plaintext_byte)
        else:
            plaintext.append(0)
    
    plaintext_hex = bytes(plaintext).hex()
    
    result = {
        "plaintext": plaintext_hex
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
