import json
import sys
import base64

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        idx = ct['message_index']
        data = base64.b64decode(ct['data'])
        ciphertexts[idx] = data
    
    # Parse known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        idx = kp['message_index']
        offset = kp['offset']
        data = base64.b64decode(kp['data'])
        if idx not in known_plaintexts:
            known_plaintexts[idx] = {}
        known_plaintexts[idx][offset] = data
    
    # Parse target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Stream cipher reuse attack
    # C0 = P0 XOR K
    # C1 = P1 XOR K
    # If we know P0, we can recover K = P0 XOR C0
    # Then P1 = C1 XOR K
    
    # Find known plaintext that overlaps with target
    for msg_idx, offsets in known_plaintexts.items():
        for offset, plaintext in offsets.items():
            # Check if this known plaintext can help us
            # We need the keystream at target_offset for target_length bytes
            
            # Get ciphertext for the message with known plaintext
            if msg_idx not in ciphertexts:
                continue
            
            ct_known = ciphertexts[msg_idx]
            
            # Extract the portion we know
            known_ct_portion = ct_known[offset:offset + len(plaintext)]
            
            # Recover keystream: K = P XOR C
            keystream = xor_bytes(plaintext, known_ct_portion)
            
            # Now use this keystream to decrypt target
            if target_msg_idx not in ciphertexts:
                continue
            
            ct_target = ciphertexts[target_msg_idx]
            
            # Check if keystream covers the target region
            keystream_start = offset
            keystream_end = offset + len(keystream)
            target_start = target_offset
            target_end = target_offset + target_length
            
            # We need keystream_start <= target_start and keystream_end >= target_end
            if keystream_start <= target_start and keystream_end >= target_end:
                # Extract the needed keystream portion
                ks_offset = target_start - keystream_start
                needed_keystream = keystream[ks_offset:ks_offset + target_length]
                
                # Decrypt target
                target_ct_portion = ct_target[target_start:target_start + target_length]
                target_plaintext = xor_bytes(target_ct_portion, needed_keystream)
                
                result = {
                    "plaintext": target_plaintext.hex()
                }
                print(json.dumps(result))
                return
    
    # If we reach here, something went wrong
    result = {"plaintext": "00" * target_length}
    print(json.dumps(result))

if __name__ == "__main__":
    main()