import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(b1, b2):
    return bytes(a ^ b for a, b in zip(b1, b2))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = hex_to_bytes(ct['data'])
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        if msg_idx not in known_plaintexts:
            known_plaintexts[msg_idx] = {}
        known_plaintexts[msg_idx][kp['offset']] = hex_to_bytes(kp['data'])
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find a known plaintext we can use to recover the keystream
    # We need a known plaintext that overlaps with our target region
    keystream = None
    
    for kp_msg_idx, kp_dict in known_plaintexts.items():
        if kp_msg_idx in ciphertexts:
            for kp_offset, kp_data in kp_dict.items():
                # Recover keystream from this known plaintext
                ct = ciphertexts[kp_msg_idx]
                kp_end = kp_offset + len(kp_data)
                
                # Extract the relevant portion of the ciphertext
                ct_segment = ct[kp_offset:kp_end]
                
                # Recover keystream: K = P ⊕ C
                ks_segment = xor_bytes(kp_data, ct_segment)
                
                # Check if this keystream segment covers our target
                if kp_msg_idx == target_msg_idx:
                    # Same message, can't use this directly for stream cipher reuse
                    # But we already have the keystream!
                    target_end = target_offset + target_length
                    if kp_offset <= target_offset and kp_end >= target_end:
                        # Extract the keystream for the target region
                        ks_for_target = ks_segment[target_offset - kp_offset:target_offset - kp_offset + target_length]
                        ct_target = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
                        plaintext = xor_bytes(ct_target, ks_for_target)
                        
                        result = {
                            "plaintext": bytes_to_hex(plaintext)
                        }
                        print(json.dumps(result))
                        return
                else:
                    # Different message - this is stream cipher reuse
                    # The keystream is the same across messages
                    # Use the recovered keystream to decrypt the target
                    target_end = target_offset + target_length
                    
                    # We need the keystream at the target position
                    # The keystream we recovered is at position kp_offset
                    if kp_offset == target_offset and len(ks_segment) >= target_length:
                        ks_for_target = ks_segment[:target_length]
                        ct_target = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
                        plaintext = xor_bytes(ct_target, ks_for_target)
                        
                        result = {
                            "plaintext": bytes_to_hex(plaintext)
                        }
                        print(json.dumps(result))
                        return

if __name__ == "__main__":
    main()
