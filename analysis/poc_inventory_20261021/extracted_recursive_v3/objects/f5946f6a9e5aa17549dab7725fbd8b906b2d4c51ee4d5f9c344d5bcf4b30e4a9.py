import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse input
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append({
            'data': bytes.fromhex(ct['data']),
            'index': ct['message_index']
        })
    
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        known_plaintexts.append({
            'data': bytes.fromhex(kp['data']),
            'index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target_index = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Find the target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['index'] == target_index:
            target_ciphertext = ct['data']
            break
    
    # Recover keystream from known plaintexts
    # We need keystream for positions [target_offset, target_offset + target_length)
    keystream = {}
    
    for kp in known_plaintexts:
        # Find the corresponding ciphertext
        ct_data = None
        for ct in ciphertexts:
            if ct['index'] == kp['index']:
                ct_data = ct['data']
                break
        
        if ct_data is None:
            continue
        
        # Recover keystream at this position
        plaintext_bytes = kp['data']
        offset = kp['offset']
        
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct_data):
                c_byte = ct_data[pos]
                k_byte = p_byte ^ c_byte
                keystream[pos] = k_byte
    
    # Decrypt target using recovered keystream
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ciphertext):
            p_byte = target_ciphertext[pos] ^ keystream[pos]
            plaintext.append(p_byte)
        else:
            # If we don't have keystream for this position, we can't decrypt
            # This shouldn't happen if the problem is solvable
            plaintext.append(0)
    
    # Output result
    result = {
        'plaintext': bytes(plaintext).hex()
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()