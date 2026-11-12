import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    # Extract the ciphertexts
    ciphertexts = {}
    for ct in instance['ciphertexts']:
        ciphertexts[ct['message_index']] = bytes.fromhex(ct['data'])
    
    # Extract known plaintexts
    known_plaintexts = {}
    for kp in instance['known_plaintexts']:
        known_plaintexts[kp['message_index']] = {
            'offset': kp['offset'],
            'data': bytes.fromhex(kp['data'])
        }
    
    # Extract target
    target = instance['target']
    target_msg_idx = target['message_index']
    target_offset = target['offset']
    target_length = target['length']
    
    # This is a stream cipher reuse attack (two-time pad)
    # If C0 = P0 XOR K and C1 = P1 XOR K (same key K)
    # Then C0 XOR C1 = P0 XOR P1
    # If we know P0, then P1 = P0 XOR C0 XOR C1
    
    # Get the known plaintext for message 0
    kp = known_plaintexts[0]
    kp_offset = kp['offset']
    kp_data = kp['data']
    
    # Get ciphertexts
    c0 = ciphertexts[0]
    c1 = ciphertexts[1]
    
    # Extract the key stream from the known plaintext
    # K = P0 XOR C0
    keystream = bytes(p ^ c for p, c in zip(kp_data, c0[kp_offset:kp_offset + len(kp_data)]))
    
    # Now decrypt the target message using the keystream
    # P1 = C1 XOR K
    target_end = target_offset + target_length
    plaintext = bytes(c ^ k for c, k in zip(c1[target_offset:target_end], keystream[target_offset:target_end]))
    
    result = {
        "plaintext": plaintext.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()