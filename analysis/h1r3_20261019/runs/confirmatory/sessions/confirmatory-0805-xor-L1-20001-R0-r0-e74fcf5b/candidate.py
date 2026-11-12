import sys
import json

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Parse known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        key = (kp['message_index'], kp['offset'])
        known_plaintexts[key] = bytes.fromhex(kp['data'])
    
    # Get target
    target = instance['target']
    target_index = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find a known plaintext we can use
    # We need a known plaintext from a different message at the same offset
    for (known_index, known_offset), known_pt in known_plaintexts.items():
        if known_index != target_index and known_offset == target_offset:
            # Extract the relevant portions
            ct_known = ciphertexts[known_index][known_offset:known_offset + target_length]
            ct_target = ciphertexts[target_index][target_offset:target_offset + target_length]
            known_pt_slice = known_pt[:target_length]
            
            # Two-time pad attack:
            # ct_known = pt_known XOR key
            # ct_target = pt_target XOR key
            # Therefore: pt_target = pt_known XOR ct_known XOR ct_target
            plaintext = xor_bytes(xor_bytes(known_pt_slice, ct_known), ct_target)
            
            result = {
                "plaintext": plaintext.hex()
            }
            print(json.dumps(result))
            return
    
    # If no solution found
    result = {"plaintext": "00" * target_length}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
