import sys
import json

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
    
    # This is a stream cipher reuse attack
    # C0 = P0 XOR K
    # C1 = P1 XOR K
    # Where K is the keystream (same for both messages)
    
    # We know P0, so we can recover K: K = P0 XOR C0
    # Then we can decrypt P1: P1 = C1 XOR K
    
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # Get the known plaintext for message 0
    known = plaintext_map[0]
    known_offset = known['offset']
    known_data = known['data']
    
    # Get ciphertexts
    c0 = ciphertext_map[0]
    c1 = ciphertext_map[target_msg_idx]
    
    # Recover the keystream from the known plaintext
    # K[known_offset : known_offset + len(known_data)] = P0 XOR C0
    keystream_start = known_offset
    keystream_end = known_offset + len(known_data)
    
    keystream = bytearray(len(c0))
    for i in range(len(known_data)):
        keystream[known_offset + i] = known_data[i] ^ c0[known_offset + i]
    
    # Now decrypt the target plaintext
    # P1[target_offset : target_offset + target_length] = C1 XOR K
    plaintext = bytearray(target_length)
    for i in range(target_length):
        plaintext[i] = c1[target_offset + i] ^ keystream[target_offset + i]
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
