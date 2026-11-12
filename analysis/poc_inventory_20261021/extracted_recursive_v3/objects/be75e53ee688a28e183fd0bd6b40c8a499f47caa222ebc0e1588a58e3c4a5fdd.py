import sys
import json
import base64
from typing import List, Dict, Tuple

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte arrays of the same length."""
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts_data = instance['ciphertexts']
    known_plaintexts_data = instance['known_plaintexts']
    target = instance['target']
    
    # Decode all ciphertexts
    ciphertexts = []
    for ct in ciphertexts_data:
        data = base64.b64decode(ct['data'])
        ciphertexts.append({
            'data': data,
            'message_index': ct['message_index']
        })
    
    # Create a mapping from message_index to ciphertext
    ct_map = {ct['message_index']: ct['data'] for ct in ciphertexts}
    
    # Decode known plaintexts
    known_plaintexts = []
    for kp in known_plaintexts_data:
        data = base64.b64decode(kp['data'])
        known_plaintexts.append({
            'data': data,
            'message_index': kp['message_index'],
            'offset': kp['offset']
        })
    
    # We're dealing with a stream cipher attack (likely reused keystream)
    # For stream ciphers: C = P XOR K, where K is the keystream
    # If we know P and C, we can recover K: K = P XOR C
    # Then for target: P_target = C_target XOR K
    
    # Recover keystream bytes from known plaintexts
    keystream = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        plaintext = kp['data']
        ciphertext = ct_map[msg_idx]
        
        # Extract the corresponding ciphertext bytes
        ct_segment = ciphertext[offset:offset + len(plaintext)]
        
        # Recover keystream: K = P XOR C
        for i, (p_byte, c_byte) in enumerate(zip(plaintext, ct_segment)):
            pos = offset + i
            if pos not in keystream:
                keystream[pos] = p_byte ^ c_byte
            else:
                # Verify consistency (all messages should use same keystream)
                assert keystream[pos] == p_byte ^ c_byte
    
    # Now decrypt the target
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    target_ciphertext = ct_map[target_msg_idx]
    
    # Decrypt using recovered keystream
    plaintext_bytes = bytearray()
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream:
            # Decrypt: P = C XOR K
            c_byte = target_ciphertext[pos]
            p_byte = c_byte ^ keystream[pos]
            plaintext_bytes.append(p_byte)
        else:
            # We don't have keystream for this position
            # This shouldn't happen if we have enough known plaintexts
            raise ValueError(f"Missing keystream at position {pos}")
    
    # Convert to hex
    plaintext_hex = plaintext_bytes.hex()
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
