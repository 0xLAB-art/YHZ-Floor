import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'index': ct['message_index']
        })
    
    # Decode known plaintexts
    known = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known.append({
            'data': data,
            'index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find ciphertext for each message index
    ct_by_index = {}
    for ct in ciphertexts:
        ct_by_index[ct['index']] = ct['data']
    
    # Recover keystream bytes using known plaintexts
    # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
    keystream = {}
    
    for kp in known:
        msg_idx = kp['index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        if msg_idx in ct_by_index:
            ciphertext = ct_by_index[msg_idx]
            for i, pt_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    # keystream = ciphertext XOR plaintext
                    keystream[pos] = ciphertext[pos] ^ pt_byte
    
    # Now decrypt the target using recovered keystream
    target_ciphertext = ct_by_index[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            # plaintext = ciphertext XOR keystream
            pt_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # If we don't have this keystream byte, we have a problem
            # Try to recover it from other known plaintexts if possible
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()