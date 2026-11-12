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
        ciphertexts.append(data)
    
    # Build keystream from known plaintexts
    # keystream[offset] = ciphertext[offset] XOR plaintext[offset]
    keystream = {}
    
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = base64.b64decode(kp['data'])
        
        ciphertext = ciphertexts[msg_idx]
        
        # Extract keystream bytes
        for i, pt_byte in enumerate(plaintext):
            pos = offset + i
            if pos < len(ciphertext):
                ct_byte = ciphertext[pos]
                ks_byte = ct_byte ^ pt_byte
                keystream[pos] = ks_byte
    
    # Decrypt target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    target_ciphertext = ciphertexts[target_msg_idx]
    
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Try to recover using crib-dragging or statistical analysis
            # For now, use 0x00 as fallback (will likely fail)
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {
        "plaintext": plaintext_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()