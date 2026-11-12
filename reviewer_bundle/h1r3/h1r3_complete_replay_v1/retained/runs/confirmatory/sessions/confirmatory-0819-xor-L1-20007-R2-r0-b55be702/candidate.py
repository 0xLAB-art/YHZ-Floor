import json
import sys
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = base64.b64decode(ct['data'])
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        known_plaintexts[kp['message_index']] = {
            'data': base64.b64decode(kp['data']),
            'offset': kp['offset']
        }
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # This is a stream cipher reuse attack (two-time pad)
    # If C1 = P1 ⊕ K and C2 = P2 ⊕ K (same key K used for both)
    # Then C1 ⊕ C2 = P1 ⊕ P2
    # And if we know P1, we can recover P2: P2 = P1 ⊕ C1 ⊕ C2
    
    # Get the known plaintext for message 0
    known_msg_idx = 0
    known_pt = known_plaintexts[known_msg_idx]['data']
    known_offset = known_plaintexts[known_msg_idx]['offset']
    
    # Get ciphertexts
    ct_known = ciphertexts[known_msg_idx]
    ct_target = ciphertexts[target_msg_idx]
    
    # Extract the target plaintext bytes
    target_plaintext = bytearray()
    
    for i in range(target_length):
        target_pos = target_offset + i
        known_pos = known_offset + i
        
        # XOR: target_pt[i] = known_pt[i] ⊕ ct_known[known_pos] ⊕ ct_target[target_pos]
        pt_byte = known_pt[i] ^ ct_known[known_pos] ^ ct_target[target_pos]
        target_plaintext.append(pt_byte)
    
    # Convert to hex
    plaintext_hex = target_plaintext.hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
