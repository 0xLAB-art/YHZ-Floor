import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Build a map of ciphertexts by message_index
    ciphertext_map = {}
    for ct in ciphertexts:
        ciphertext_map[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Build a map of known plaintexts by message_index
    plaintext_map = {}
    for kp in known_plaintexts:
        plaintext_map[kp['message_index']] = {
            'offset': kp['offset'],
            'data': bytes.fromhex(kp['data'])
        }
    
    # This is a stream cipher key reuse attack
    # If C0 = P0 XOR K and C1 = P1 XOR K, then C0 XOR C1 = P0 XOR P1
    # If we know P0, we can recover K = C0 XOR P0
    # Then P1 = C1 XOR K
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Find a known plaintext that we can use to recover the key
    # We need a known plaintext for a different message (or same message at different offset)
    
    # Get the target ciphertext
    target_ciphertext = ciphertext_map[target_msg_idx]
    
    # Extract the portion we need to decrypt
    target_ct_portion = target_ciphertext[target_offset:target_offset + target_length]
    
    # Find a known plaintext that overlaps with our target region
    # We need to recover the keystream at positions [target_offset, target_offset + target_length)
    
    # Look for a known plaintext from a different message that can help us
    for kp_msg_idx, kp_info in plaintext_map.items():
        kp_offset = kp_info['offset']
        kp_data = kp_info['data']
        kp_length = len(kp_data)
        
        # Get the ciphertext for this known plaintext message
        if kp_msg_idx not in ciphertext_map:
            continue
        
        kp_ciphertext = ciphertext_map[kp_msg_idx]
        
        # Extract the ciphertext portion corresponding to the known plaintext
        kp_ct_portion = kp_ciphertext[kp_offset:kp_offset + kp_length]
        
        # Recover the keystream: K = P XOR C
        keystream = bytes(p ^ c for p, c in zip(kp_data, kp_ct_portion))
        
        # Check if this keystream overlaps with our target
        # In a stream cipher with key reuse, the keystream at position i is the same
        # for all messages that use the same key
        
        # We need to check if the keystream positions match
        # keystream covers positions [kp_offset, kp_offset + kp_length)
        # target needs positions [target_offset, target_offset + target_length)
        
        # For simplicity, if they're at the same offset and we're attacking different messages
        if kp_offset == target_offset and kp_msg_idx != target_msg_idx:
            # We can directly use the keystream
            plaintext = bytes(c ^ k for c, k in zip(target_ct_portion, keystream[:target_length]))
            result = {"plaintext": plaintext.hex()}
            print(json.dumps(result))
            return
    
    # If no direct match, we might need to handle partial overlaps or reconstruct
    # Let's try a more general approach: recover as much keystream as possible
    
    # Build the keystream for all positions we know
    max_length = max(len(ct) for ct in ciphertext_map.values())
    keystream_known = {}
    
    for kp_msg_idx, kp_info in plaintext_map.items():
        if kp_msg_idx not in ciphertext_map:
            continue
        
        kp_offset = kp_info['offset']
        kp_data = kp_info['data']
        kp_ciphertext = ciphertext_map[kp_msg_idx]
        
        for i, (p, c) in enumerate(zip(kp_data, kp_ciphertext[kp_offset:kp_offset + len(kp_data)])):
            pos = kp_offset + i
            keystream_known[pos] = p ^ c
    
    # Now decrypt the target using the known keystream
    plaintext = []
    for i in range(target_length):
        pos = target_offset + i
        if pos in keystream_known:
            plaintext.append(target_ct_portion[i] ^ keystream_known[pos])
        else:
            # This shouldn't happen if the instance is solvable
            plaintext.append(0)
    
    result = {"plaintext": bytes(plaintext).hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()