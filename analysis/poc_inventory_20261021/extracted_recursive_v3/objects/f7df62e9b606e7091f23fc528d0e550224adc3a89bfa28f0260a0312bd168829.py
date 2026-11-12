import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = instance['ciphertexts']
    target = instance['target']
    known_plaintexts = instance.get('known_plaintexts', [])
    
    # Convert hex ciphertexts to bytes
    ct_bytes = []
    for ct in ciphertexts:
        ct_bytes.append(bytes.fromhex(ct['data']))
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # This appears to be a many-time pad attack scenario
    # Multiple messages encrypted with the same keystream (stream cipher reuse)
    
    # With no known plaintexts and 8 ciphertexts, we need to use statistical analysis
    # However, without additional constraints or known plaintexts, we cannot uniquely
    # determine the plaintext
    
    # Check if we have any known plaintexts
    if not known_plaintexts:
        # No known plaintexts - cannot uniquely determine the message
        result = {
            "status": "UNDERDETERMINED",
            "reason": "No known plaintexts provided; cannot uniquely recover plaintext from ciphertexts alone without additional cryptanalytic constraints"
        }
    else:
        # Even with some known plaintexts, we need to check if they provide
        # enough information to recover the target region
        
        # Build keystream from known plaintexts
        keystream = {}
        for kp in known_plaintexts:
            msg_idx = kp['message_index']
            offset = kp['offset']
            plaintext = bytes.fromhex(kp['data'])
            
            for i, p_byte in enumerate(plaintext):
                pos = offset + i
                k_byte = ct_bytes[msg_idx][pos] ^ p_byte
                if pos not in keystream:
                    keystream[pos] = k_byte
        
        # Check if we have all keystream bytes for target region
        target_positions = set(range(target_offset, target_offset + target_length))
        known_positions = set(keystream.keys())
        
        if target_positions.issubset(known_positions):
            # We can recover the target
            plaintext_bytes = bytes([ct_bytes[target_msg_idx][pos] ^ keystream[pos] 
                                    for pos in range(target_offset, target_offset + target_length)])
            result = {
                "status": "RECOVERED",
                "plaintext": plaintext_bytes.hex()
            }
        else:
            missing = len(target_positions - known_positions)
            result = {
                "status": "UNDERDETERMINED",
                "reason": f"Known plaintexts do not cover target region; {missing} bytes of keystream unknown"
            }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()