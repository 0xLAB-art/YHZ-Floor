import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Build a map of ciphertexts by message_index
    ciphertext_map = {}
    for ct in ciphertexts:
        ciphertext_map[ct['message_index']] = hex_to_bytes(ct['data'])
    
    # Extract keystream from known plaintext
    # For stream cipher: ciphertext = plaintext XOR keystream
    # So: keystream = plaintext XOR ciphertext
    keystream_segments = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = hex_to_bytes(kp['data'])
        ciphertext = ciphertext_map[msg_idx]
        
        # Extract the relevant ciphertext segment
        ct_segment = ciphertext[offset:offset + len(plaintext)]
        
        # Recover keystream segment
        keystream_segment = xor_bytes(plaintext, ct_segment)
        
        if msg_idx not in keystream_segments:
            keystream_segments[msg_idx] = {}
        keystream_segments[msg_idx][offset] = keystream_segment
    
    # Now decrypt the target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ciphertext_map[target_msg_idx]
    target_ct_segment = target_ciphertext[target_offset:target_offset + target_length]
    
    # Check if we have keystream for the target message at the target offset
    # In many stream cipher attacks with keystream reuse, the same keystream
    # is used across different messages. Let's try using keystream from message 0
    # at the same offset position
    
    # Try to find keystream that overlaps with target position
    keystream = None
    for msg_idx, segments in keystream_segments.items():
        for offset, ks_segment in segments.items():
            if offset <= target_offset < offset + len(ks_segment):
                # We have keystream covering the start
                start_in_ks = target_offset - offset
                available_length = len(ks_segment) - start_in_ks
                if available_length >= target_length:
                    keystream = ks_segment[start_in_ks:start_in_ks + target_length]
                    break
            elif target_offset == offset:
                keystream = ks_segment[:target_length]
                break
        if keystream:
            break
    
    # If keystream reuse across messages (common attack scenario)
    # The keystream from message 0 at offset 0 can decrypt message 1 at offset 0
    if keystream is None and 0 in keystream_segments and 0 in keystream_segments[0]:
        ks = keystream_segments[0][0]
        if target_offset < len(ks) and target_offset + target_length <= len(ks):
            keystream = ks[target_offset:target_offset + target_length]
    
    # Decrypt target
    if keystream and len(keystream) == target_length:
        plaintext = xor_bytes(target_ct_segment, keystream)
    else:
        # Fallback: assume keystream from message 0 offset 0 is reused
        if 0 in keystream_segments and 0 in keystream_segments[0]:
            keystream = keystream_segments[0][0][target_offset:target_offset + target_length]
            plaintext = xor_bytes(target_ct_segment, keystream)
        else:
            plaintext = b'\x00' * target_length
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(plaintext)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()