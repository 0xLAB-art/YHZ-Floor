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
        idx = ct['message_index']
        data = base64.b64decode(ct['data'])
        ct_map[idx] = data
    
    # Decode known plaintexts
    kp_map = {}
    for kp in known_plaintexts:
        idx = kp['message_index']
        offset = kp['offset']
        data = base64.b64decode(kp['data'])
        if idx not in kp_map:
            kp_map[idx] = {}
        kp_map[idx][offset] = data
    
    # Extract target information
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # This is a stream cipher reuse attack (two-time pad)
    # If we have plaintext P0 at offset o for message m0
    # and ciphertext C0 = P0 XOR K (where K is the keystream at offset o)
    # then K = P0 XOR C0
    # For message m1 at the same offset: C1 = P1 XOR K
    # So P1 = C1 XOR K = C1 XOR P0 XOR C0
    
    # Find known plaintext that we can use
    known_msg_idx = None
    known_offset = None
    known_plaintext = None
    
    for msg_idx, offsets in kp_map.items():
        for offset, plaintext in offsets.items():
            known_msg_idx = msg_idx
            known_offset = offset
            known_plaintext = plaintext
            break
        if known_msg_idx is not None:
            break
    
    # Get the ciphertexts
    known_ct = ct_map[known_msg_idx]
    target_ct = ct_map[target_msg_idx]
    
    # Extract the keystream from known plaintext
    # K = P XOR C at the known offset
    keystream_start = known_offset
    keystream_length = len(known_plaintext)
    keystream = bytes(known_plaintext[i] ^ known_ct[known_offset + i] 
                     for i in range(keystream_length))
    
    # Now decrypt the target using the keystream
    # P_target = C_target XOR K
    result = bytes(target_ct[target_offset + i] ^ keystream[i] 
                   for i in range(target_length))
    
    # Convert to lowercase hex
    plaintext_hex = result.hex()
    
    print(json.dumps({"plaintext": plaintext_hex}))

if __name__ == "__main__":
    main()
