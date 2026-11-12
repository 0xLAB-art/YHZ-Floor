import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = {ct['message_index']: hex_to_bytes(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Get the known plaintext for message 0
    known_pt = None
    known_msg_idx = None
    known_offset = None
    
    for kp in known_plaintexts:
        known_pt = hex_to_bytes(kp['data'])
        known_msg_idx = kp['message_index']
        known_offset = kp['offset']
    
    # Get target information
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Extract relevant portions of ciphertexts
    c_known = ciphertexts[known_msg_idx][known_offset:known_offset + len(known_pt)]
    c_target = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
    
    # If this is a stream cipher with keystream reuse:
    # C0 = P0 ⊕ K
    # C1 = P1 ⊕ K
    # Therefore: K = C0 ⊕ P0
    # And: P1 = C1 ⊕ K = C1 ⊕ C0 ⊕ P0
    
    keystream = xor_bytes(c_known, known_pt)
    target_plaintext = xor_bytes(c_target, keystream[:target_length])
    
    # Output result
    result = {
        "plaintext": bytes_to_hex(target_plaintext)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()