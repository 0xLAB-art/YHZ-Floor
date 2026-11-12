import sys
import json
import base64

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = base64.b64decode(ct['data'])
    
    # Parse known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = base64.b64decode(kp['data'])
        if msg_idx not in known_plaintexts:
            known_plaintexts[msg_idx] = {}
        known_plaintexts[msg_idx][offset] = data
    
    # Get target
    target_msg_idx = instance['target']['message_index']
    target_offset = instance['target']['offset']
    target_length = instance['target']['length']
    
    # Find a known plaintext we can use
    # We need known plaintext from a different message at the same offset
    result_bytes = bytearray(target_length)
    
    for known_msg_idx in known_plaintexts:
        if known_msg_idx == target_msg_idx:
            continue
        
        if target_offset in known_plaintexts[known_msg_idx]:
            known_pt = known_plaintexts[known_msg_idx][target_offset]
            known_ct = ciphertexts[known_msg_idx][target_offset:target_offset + target_length]
            target_ct = ciphertexts[target_msg_idx][target_offset:target_offset + target_length]
            
            # XOR attack: P_target = P_known ⊕ C_known ⊕ C_target
            for i in range(target_length):
                result_bytes[i] = known_pt[i] ^ known_ct[i] ^ target_ct[i]
            
            break
    
    # Convert to hex
    result_hex = result_bytes.hex()
    
    # Output
    output = {"plaintext": result_hex}
    print(json.dumps(output))

if __name__ == "__main__":
    main()
