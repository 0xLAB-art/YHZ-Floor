import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    # This is a many-time pad attack
    # XOR property: C1 XOR C2 = (P1 XOR K) XOR (P2 XOR K) = P1 XOR P2
    # If we know P1, we can recover P2
    
    # Build keystream from known plaintexts
    keystream = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext_bytes = bytes.fromhex(kp['data'])
        
        # For each byte of known plaintext, recover keystream
        for i, p_byte in enumerate(plaintext_bytes):
            pos = offset + i
            c_byte = ct_bytes[msg_idx][pos]
            k_byte = c_byte ^ p_byte
            
            if pos not in keystream:
                keystream[pos] = k_byte
            else:
                # Verify consistency
                if keystream[pos] != k_byte:
                    # Inconsistency - this shouldn't happen with correct data
                    pass
    
    # Now decrypt the target message using the recovered keystream
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    result = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            c_byte = ct_bytes[target_msg_idx][pos]
            p_byte = c_byte ^ keystream[pos]
            result.append(p_byte)
        else:
            # Keystream byte not recovered - this is a problem
            # Try to infer from crib dragging or use heuristics
            result.append(0)
    
    plaintext_hex = bytes(result).hex()
    
    output = {
        "plaintext": plaintext_hex
    }
    
    print(json.dumps(output))

if __name__ == '__main__':
    main()