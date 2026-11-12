import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse input
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': bytes.fromhex(ct['data']),
            'message_index': ct['message_index']
        })
    
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        known_plaintexts.append({
            'data': bytes.fromhex(kp['data']),
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # This is a stream cipher reuse attack (many-time pad)
    # C_i = P_i XOR K, where K is the reused keystream
    # If we know P_i at some position, we can recover K at that position
    # Then use K to decrypt other messages at the same position
    
    # Find maximum ciphertext length
    max_len = max(len(ct['data']) for ct in ciphertexts)
    
    # Recover keystream byte by byte using known plaintexts
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
        
        if ciphertext is None:
            continue
        
        # Recover keystream at these positions
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                k_byte = ciphertext[pos] ^ p_byte
                keystream[pos] = k_byte
    
    # Now decrypt the target using the recovered keystream
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = ct['data']
            break
    
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            plaintext_byte = target_ciphertext[pos] ^ keystream[pos]
            result.append(plaintext_byte)
        else:
            # Should not happen if we have enough known plaintexts
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
