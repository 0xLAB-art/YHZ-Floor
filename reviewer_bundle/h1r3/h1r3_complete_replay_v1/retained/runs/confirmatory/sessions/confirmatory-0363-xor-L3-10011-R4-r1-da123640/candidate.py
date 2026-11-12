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
    
    # This appears to be a many-time pad attack (stream cipher key reuse)
    # When the same keystream is used for multiple messages:
    # C1 = M1 XOR K
    # C2 = M2 XOR K
    # Therefore: C1 XOR C2 = M1 XOR M2
    
    # First, recover the keystream at known positions
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        # Extract corresponding ciphertext bytes
        ct = ct_bytes[msg_idx]
        
        # Recover keystream: K = C XOR M
        for i, pb in enumerate(plaintext_bytes):
            pos = offset + i
            if pos < len(ct):
                keystream[pos] = ct[pos] ^ pb
    
    # Now use the recovered keystream to decrypt the target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ct = ct_bytes[target_msg_idx]
    
    # Decrypt using known keystream
    plaintext_bytes = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream and pos < len(target_ct):
            # Decrypt: M = C XOR K
            plaintext_bytes.append(target_ct[pos] ^ keystream[pos])
        else:
            # If we don't have the keystream at this position, try to deduce it
            # from other ciphertexts and known plaintexts
            
            # Try to find another message with known plaintext at this position
            found = False
            for kp in known_plaintexts:
                kp_msg_idx = kp['message_index']
                kp_offset = kp['offset']
                kp_data = bytes.fromhex(kp['data'])
                kp_length = len(kp_data)
                
                if kp_offset <= pos < kp_offset + kp_length:
                    # This known plaintext covers position pos
                    kp_pos_in_data = pos - kp_offset
                    kp_ct = ct_bytes[kp_msg_idx]
                    
                    if pos < len(kp_ct):
                        # Recover keystream from this known plaintext
                        k = kp_ct[pos] ^ kp_data[kp_pos_in_data]
                        keystream[pos] = k
                        
                        # Decrypt target
                        if pos < len(target_ct):
                            plaintext_bytes.append(target_ct[pos] ^ k)
                            found = True
                            break
            
            if not found:
                # Still no keystream - shouldn't happen if problem is solvable
                plaintext_bytes.append(0)
    
    # Convert to hex
    plaintext_hex = ''.join(f'{b:02x}' for b in plaintext_bytes)
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
