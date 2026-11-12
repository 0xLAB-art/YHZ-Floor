#!/usr/bin/env python3
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
    
    target = instance['target']
    ciphertexts = {c['message_index']: hex_to_bytes(c['data']) for c in instance['ciphertexts']}
    known_plaintexts = {kp['message_index']: {'offset': kp['offset'], 'data': hex_to_bytes(kp['data'])} for kp in instance['known_plaintexts']}
    
    # Extract known plaintext for message 0
    known_pt = known_plaintexts[0]
    pt0_offset = known_pt['offset']
    pt0_data = known_pt['data']
    
    # Get corresponding ciphertext for message 0
    ct0 = ciphertexts[0]
    
    # Recover keystream: K = P0 ⊕ C0
    keystream = xor_bytes(pt0_data, ct0[pt0_offset:pt0_offset + len(pt0_data)])
    
    # Get target ciphertext
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    ct_target = ciphertexts[target_msg_idx]
    
    # Decrypt: P1 = C1 ⊕ K
    plaintext = xor_bytes(ct_target[target_offset:target_offset + target_length], 
                          keystream[target_offset:target_offset + target_length])
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(plaintext)
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()