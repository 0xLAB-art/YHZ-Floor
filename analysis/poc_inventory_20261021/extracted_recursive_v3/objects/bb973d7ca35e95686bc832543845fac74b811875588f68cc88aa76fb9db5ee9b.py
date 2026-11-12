import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': base64.b64decode(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Build keystream recovery map: (message_index, offset) -> keystream_byte
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        message_index = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = base64.b64decode(kp['data'])
        
        # Find the ciphertext for this message
        ciphertext_data = None
        for ct in ciphertexts:
            if ct['message_index'] == message_index:
                ciphertext_data = ct['data']
                break
        
        if ciphertext_data is None:
            continue
        
        # Recover keystream bytes: keystream = plaintext XOR ciphertext
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext_data):
                ct_byte = ciphertext_data[pos]
                ks_byte = pt_byte ^ ct_byte
                keystream[(message_index, pos)] = ks_byte
    
    # Now decrypt the target
    target = instance['target']
    target_message_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_message_index:
            target_ciphertext = ct['data']
            break
    
    # Decrypt using recovered keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        
        # Try to find keystream byte from any message at this offset
        ks_byte = None
        
        # First try from the same message
        if (target_message_index, pos) in keystream:
            ks_byte = keystream[(target_message_index, pos)]
        else:
            # If stream cipher reuses keystream across messages at same offset
            for msg_idx in range(len(ciphertexts)):
                if (msg_idx, pos) in keystream:
                    ks_byte = keystream[(msg_idx, pos)]
                    break
        
        if ks_byte is not None and pos < len(target_ciphertext):
            pt_byte = target_ciphertext[pos] ^ ks_byte
            plaintext_bytes.append(pt_byte)
        else:
            # Can't decrypt this byte
            plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
