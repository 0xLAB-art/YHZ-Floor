import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # XOR of two ciphertexts gives XOR of two plaintexts: C1 ⊕ C2 = P1 ⊕ P2
    # If we know P1, we can recover the keystream: K = C1 ⊕ P1
    # Then we can decrypt any other ciphertext: P = C ⊕ K
    
    # Build keystream from known plaintexts
    max_len = max(len(ct) for ct in ct_bytes)
    keystream = [None] * max_len
    
    # For each known plaintext, recover the keystream at those positions
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        pt_data = bytes.fromhex(kp['data'])
        
        ct = ct_bytes[msg_idx]
        
        # XOR plaintext with ciphertext to get keystream
        for i, pt_byte in enumerate(pt_data):
            pos = offset + i
            if pos < len(ct):
                ks_byte = ct[pos] ^ pt_byte
                keystream[pos] = ks_byte
    
    # Now decrypt the target message using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos < len(target_ct) and keystream[pos] is not None:
            pt_byte = target_ct[pos] ^ keystream[pos]
            plaintext.append(pt_byte)
        else:
            # Should not happen if we have enough known plaintexts
            plaintext.append(0)
    
    plaintext_hex = bytes(plaintext).hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
