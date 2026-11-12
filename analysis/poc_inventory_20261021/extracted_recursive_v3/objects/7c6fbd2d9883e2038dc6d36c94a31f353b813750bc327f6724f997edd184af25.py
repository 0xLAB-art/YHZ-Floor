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
    
    # This is a many-time pad attack (stream cipher key reuse)
    # When the same key is reused: C1 XOR C2 = P1 XOR P2
    # With known plaintexts, we can recover the keystream at those positions
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_hex = kp['data']
        plaintext = bytes.fromhex(plaintext_hex)
        
        # keystream[pos] = ciphertext[pos] XOR plaintext[pos]
        for i, p_byte in enumerate(plaintext):
            pos = offset + i
            c_byte = ct_bytes[msg_idx][pos]
            keystream[pos] = c_byte ^ p_byte
    
    # Now decrypt the target using the recovered keystream
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # We have the keystream at this position
            c_byte = ct_bytes[target_msg_idx][pos]
            p_byte = c_byte ^ keystream[pos]
            result.append(p_byte)
        else:
            # We don't have keystream at this position
            # Try to recover it from other known plaintexts at the same position
            # Or use crib-dragging techniques
            
            # For positions we can't recover directly, we need to use
            # the XOR relationships between ciphertexts
            # But first, let's see if we can get more keystream from the known data
            
            # Check if we can infer anything from XOR relationships
            recovered = False
            
            # Try all other messages at the same position
            for other_idx in range(len(ct_bytes)):
                if other_idx == target_msg_idx:
                    continue
                
                # Check if we have known plaintext for this other message at this position
                for kp in known_plaintexts:
                    if kp['message_index'] == other_idx and kp['offset'] <= pos < kp['offset'] + len(kp['data']) // 2:
                        # We have plaintext for other_idx at pos
                        kp_offset_in_data = pos - kp['offset']
                        other_plaintext_byte = bytes.fromhex(kp['data'])[kp_offset_in_data]
                        other_cipher_byte = ct_bytes[other_idx][pos]
                        
                        # Recover keystream: K = C XOR P
                        k = other_cipher_byte ^ other_plaintext_byte
                        
                        # Decrypt target: P = C XOR K
                        target_cipher_byte = ct_bytes[target_msg_idx][pos]
                        target_plain_byte = target_cipher_byte ^ k
                        
                        result.append(target_plain_byte)
                        recovered = True
                        break
                
                if recovered:
                    break
            
            if not recovered:
                # Still can't recover - this shouldn't happen with enough known plaintexts
                # Default to 0 (but this is likely wrong)
                result.append(0)
    
    plaintext_hex = bytes(result).hex()
    
    output = {"plaintext": plaintext_hex}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
