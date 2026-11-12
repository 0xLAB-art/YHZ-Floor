import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    target = instance['target']
    
    # Decode ciphertexts
    ct_map = {}
    for ct in ciphertexts:
        ct_map[ct['message_index']] = base64.b64decode(ct['data'])
    
    # Decode known plaintexts
    kp_map = {}
    for kp in known_plaintexts:
        msg_idx = kp['message_index']
        offset = kp['offset']
        data = base64.b64decode(kp['data'])
        if msg_idx not in kp_map:
            kp_map[msg_idx] = {}
        kp_map[msg_idx][offset] = data
    
    # Extract what we know
    # We have ciphertext for message 0 and message 1
    # We have plaintext for message 0 at offset 0
    
    # For stream cipher attacks (XOR-based):
    # C0 = P0 XOR K
    # C1 = P1 XOR K
    # If we know P0, we can recover K = P0 XOR C0
    # Then P1 = C1 XOR K
    
    known_msg_idx = 0
    known_offset = 0
    known_plaintext = kp_map[known_msg_idx][known_offset]
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get ciphertexts
    c0 = ct_map[known_msg_idx]
    c1 = ct_map[target_msg_idx]
    
    # Recover keystream from known plaintext
    # K = P0 XOR C0
    keystream = bytes(p ^ c for p, c in zip(known_plaintext, c0[known_offset:known_offset+len(known_plaintext)]))
    
    # Recover target plaintext
    # P1 = C1 XOR K
    target_plaintext = bytes(c ^ k for c, k in zip(c1[target_offset:target_offset+target_length], keystream))
    
    # Output as lowercase hex
    result = {"plaintext": target_plaintext.hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
