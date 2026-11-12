import sys
import json
import base64
from typing import List, Dict, Tuple

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings of equal length."""
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse input
    ciphertexts = []
    for ct in instance['ciphertexts']:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    known_plaintexts = []
    for kp in instance['known_plaintexts']:
        data = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': data,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find target ciphertext
    target_ciphertext = None
    for ct in ciphertexts:
        if ct['message_index'] == target_msg_idx:
            target_ciphertext = ct['data']
            break
    
    # Build a keystream from known plaintexts
    # In a stream cipher, C = P XOR K, so K = P XOR C
    max_len = max(kp['offset'] + len(kp['data']) for kp in known_plaintexts)
    max_len = max(max_len, target_offset + target_length)
    
    # For each ciphertext, track what we know about the keystream
    keystream_parts = {}
    
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['data']
        
        # Find corresponding ciphertext
        ciphertext = None
        for ct in ciphertexts:
            if ct['message_index'] == msg_idx:
                ciphertext = ct['data']
                break
        
        if ciphertext is None:
            continue
        
        # Extract the ciphertext portion
        ct_portion = ciphertext[offset:offset + len(plaintext)]
        
        # Compute keystream: K = P XOR C
        keystream = xor_bytes(plaintext, ct_portion)
        
        # Store keystream
        if msg_idx not in keystream_parts:
            keystream_parts[msg_idx] = {}
        
        for i, k in enumerate(keystream):
            keystream_parts[msg_idx][offset + i] = k
    
    # Check if we're dealing with a stream cipher that reuses keystream
    # or if each message has its own keystream
    # Let's assume it's a many-time pad where the same keystream is used
    
    # Merge all keystream parts (assuming same key used for all)
    keystream = {}
    for msg_idx in keystream_parts:
        for pos, k in keystream_parts[msg_idx].items():
            if pos not in keystream:
                keystream[pos] = k
            # If there's a conflict, we might have different keys per message
    
    # Try to decrypt target using the merged keystream
    target_ct_portion = target_ciphertext[target_offset:target_offset + target_length]
    plaintext_bytes = bytearray(target_length)
    
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            plaintext_bytes[i] = target_ct_portion[i] ^ keystream[pos]
        else:
            # We don't have keystream for this position
            # Try to infer it from other messages
            plaintext_bytes[i] = 0  # placeholder
    
    # Check if we have complete coverage
    missing_positions = []
    for i in range(target_length):
        pos = target_offset + i
        if pos not in keystream:
            missing_positions.append(pos)
    
    # If we have missing positions, we need another approach
    # Perhaps each message uses the same keystream (many-time pad)
    if missing_positions:
        # Try using keystream from same position in other messages
        # Build a unified keystream
        unified_keystream = [None] * (target_offset + target_length)
        
        for msg_idx in keystream_parts:
            for pos, k in keystream_parts[msg_idx].items():
                if pos < len(unified_keystream):
                    if unified_keystream[pos] is None:
                        unified_keystream[pos] = k
        
        # Decrypt target
        for i in range(target_length):
            pos = target_offset + i
            if unified_keystream[pos] is not None:
                plaintext_bytes[i] = target_ct_portion[i] ^ unified_keystream[pos]
    
    # Convert to hex
    plaintext_hex = plaintext_bytes.hex()
    
    # Output
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
