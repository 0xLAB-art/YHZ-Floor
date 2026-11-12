import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) 
                   for ct in instance['ciphertexts']}
    known_plaintexts = {kp['message_index']: {
        'data': bytes.fromhex(kp['data']),
        'offset': kp['offset']
    } for kp in instance['known_plaintexts']}
    target = instance['target']
    
    # This is a stream cipher reuse attack (two-time pad)
    # If the same keystream is used for multiple messages:
    # C1 = P1 XOR K
    # C2 = P2 XOR K
    # Therefore: C1 XOR C2 = P1 XOR P2
    # If we know P1, we can recover P2: P2 = P1 XOR C1 XOR C2
    
    known_msg_idx = list(known_plaintexts.keys())[0]
    known_pt = known_plaintexts[known_msg_idx]['data']
    known_offset = known_plaintexts[known_msg_idx]['offset']
    known_ct = ciphertexts[known_msg_idx]
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    target_ct = ciphertexts[target_msg_idx]
    
    # Extract the keystream from the known plaintext/ciphertext pair
    keystream_start = known_offset
    keystream_end = known_offset + len(known_pt)
    keystream = bytes(known_pt[i] ^ known_ct[keystream_start + i] 
                     for i in range(len(known_pt)))
    
    # Use the keystream to decrypt the target
    plaintext_bytes = bytes(target_ct[target_offset + i] ^ keystream[i]
                           for i in range(target_length))
    
    result = {
        "plaintext": plaintext_bytes.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()