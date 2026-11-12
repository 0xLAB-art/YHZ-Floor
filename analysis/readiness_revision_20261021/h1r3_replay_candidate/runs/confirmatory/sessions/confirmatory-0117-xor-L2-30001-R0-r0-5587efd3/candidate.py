import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = []
    for ct in instance['ciphertexts']:
        ciphertexts.append(bytes.fromhex(ct['data']))
    
    # Initialize keystream recovery
    # Assume stream cipher with reused keystream
    max_len = max(len(ct) for ct in ciphertexts)
    keystream = [None] * max_len
    
    # Recover keystream from known plaintexts
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        ciphertext = ciphertexts[msg_idx]
        
        # XOR plaintext with ciphertext to get keystream
        for i, pt_byte in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ciphertext):
                ct_byte = ciphertext[pos]
                ks_byte = pt_byte ^ ct_byte
                
                # Verify consistency if we already have this keystream byte
                if keystream[pos] is not None:
                    if keystream[pos] != ks_byte:
                        # Inconsistency - not a simple stream cipher reuse
                        pass
                keystream[pos] = ks_byte
    
    # Decrypt target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    target_ciphertext = ciphertexts[target_msg_idx]
    plaintext_bytes = []
    
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ciphertext) and keystream[pos] is not None:
            ct_byte = target_ciphertext[pos]
            pt_byte = ct_byte ^ keystream[pos]
            plaintext_bytes.append(pt_byte)
        else:
            # Can't decrypt this byte
            plaintext_bytes.append(0)
    
    plaintext_hex = bytes(plaintext_bytes).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
