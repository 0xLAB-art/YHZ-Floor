import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a mapping of message_index -> ciphertext
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build a mapping of message_index -> known plaintext bytes
    pt_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if msg_idx not in pt_map:
            pt_map[msg_idx] = {}
        for i, b in enumerate(data):
            pt_map[msg_idx][offset + i] = b
    
    # Extract what we need
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # This is a two-time pad attack
    # For stream ciphers with key reuse: C1 = P1 XOR K, C2 = P2 XOR K
    # Therefore: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can recover P2: P2 = P1 XOR C1 XOR C2
    
    # Find the known plaintext message
    known_msg_idx = list(pt_map.keys())[0]
    
    # Get ciphertexts
    ct_known = ct_map[known_msg_idx]
    ct_target = ct_map[target_msg_idx]
    
    # Recover the target plaintext
    plaintext = bytearray()
    for i in range(target_offset, target_offset + target_length):
        # P_target[i] = P_known[i] XOR C_known[i] XOR C_target[i]
        p_known = pt_map[known_msg_idx][i]
        c_known = ct_known[i]
        c_target = ct_target[i]
        p_target = p_known ^ c_known ^ c_target
        plaintext.append(p_target)
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
