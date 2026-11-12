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
    
    # Find the target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = ct['data']
            break
    
    # This is a stream cipher reuse attack (same keystream for all messages)
    # C_i = P_i XOR K where K is the keystream
    # If we know P_i at some position, we can recover K at that position: K = P_i XOR C_i
    # Then we can decrypt any other message at that position: P_j = C_j XOR K
    
    # Build the keystream from known plaintexts
    max_len = max(ct['data'].__len__() for ct in ciphertexts)
    keystream = [None] * max_len
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = kp['data']
        
        # Find the ciphertext for this message
        ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext:
            # Recover keystream bytes
            for i, p_byte in enumerate(plaintext_bytes):
                pos = offset + i
                if pos < len(ciphertext):
                    k_byte = ciphertext[pos] ^ p_byte
                    keystream[pos] = k_byte
    
    # Now decrypt the target using the recovered keystream
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            plaintext_byte = target_ciphertext[pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # If we don't have the keystream at this position, we need to use
            # other techniques or the keystream might not be fully recoverable
            # For now, try to infer from other ciphertexts if possible
            result.append(0)
    
    # Convert to hex
    plaintext_hex = bytes(result).hex()
    
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()