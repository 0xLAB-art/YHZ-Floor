import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Parse the instance
    ciphertexts = {ct['message_index']: bytes.fromhex(ct['data']) 
                   for ct in instance['ciphertexts']}
    
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        idx = kp['message_index']
        offset = kp['offset']
        data = bytes.fromhex(kp['data'])
        if idx not in known_plaintexts:
            known_plaintexts[idx] = {}
        known_plaintexts[idx][offset] = data
    
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # This is a stream cipher reuse attack
    # C0 = P0 XOR K
    # C1 = P1 XOR K
    # If we know P0, we can recover K = P0 XOR C0
    # Then recover P1 = C1 XOR K
    
    # Find a known plaintext we can use
    known_msg_idx = list(known_plaintexts.keys())[0]
    known_offset = list(known_plaintexts[known_msg_idx].keys())[0]
    known_plaintext = known_plaintexts[known_msg_idx][known_offset]
    
    # Get corresponding ciphertext
    known_ciphertext = ciphertexts[known_msg_idx]
    
    # Recover the keystream for this region
    keystream_start = known_offset
    keystream_length = len(known_plaintext)
    keystream = bytes(known_plaintext[i] ^ known_ciphertext[keystream_start + i] 
                     for i in range(keystream_length))
    
    # Now decrypt the target using the recovered keystream
    target_ciphertext = ciphertexts[target_msg_idx]
    
    # Check if we have enough keystream
    if target_offset >= keystream_start and target_offset + target_length <= keystream_start + keystream_length:
        # We can decrypt directly
        keystream_offset = target_offset - keystream_start
        plaintext = bytes(target_ciphertext[target_offset + i] ^ keystream[keystream_offset + i] 
                         for i in range(target_length))
    else:
        # This shouldn't happen based on the instance structure
        plaintext = bytes(target_length)
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()