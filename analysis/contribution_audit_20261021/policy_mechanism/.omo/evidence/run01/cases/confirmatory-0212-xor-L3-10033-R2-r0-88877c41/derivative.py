import sys
import json
import base64


def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': base64.b64decode(ct['data']),
            'message_index': ct['message_index']
        })
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        known_plaintexts.append({
            'data': base64.b64decode(kp['data']),
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get target ciphertext
    target_ct = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ct = ct['data']
            break
    
    # Build keystream from known plaintexts
    # For stream cipher reuse: C = P XOR K, so K = P XOR C
    max_len = max(len(ct['data']) for ct in ciphertexts)
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        # Find corresponding ciphertext
        ct_data = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ct_data = ct['data']
                break
        
        if ct_data is None:
            continue
        
        # Extract keystream bytes
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct_data):
                c_byte = ct_data[pos]
                k_byte = p_byte ^ c_byte
                keystream[pos] = k_byte
    
    # Decrypt target using recovered keystream
    plaintext = bytearray()
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            p_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(p_byte)
        else:
            # If we don't have keystream, we need to try to recover it
            # This shouldn't happen with proper known plaintexts
            plaintext.append(0)
    
    # Convert to hex
    plaintext_hex = plaintext.hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
