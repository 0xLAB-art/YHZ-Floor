import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertext for message_index 0 and 1
    c0_data = None
    c1_data = None
    
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            c0_data = ct['data']
        elif ct['message_index'] == 1:
            c1_data = ct['data']
    
    # Find the known plaintext for message_index 0
    p0_data = None
    p0_offset = None
    
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            p0_data = kp['data']
            p0_offset = kp['offset']
    
    # Convert hex strings to bytes
    c0 = bytes.fromhex(c0_data)
    c1 = bytes.fromhex(c1_data)
    p0 = bytes.fromhex(p0_data)
    
    # This is a stream cipher attack (likely reused keystream)
    # c0 = p0 XOR k
    # c1 = p1 XOR k
    # Therefore: k = c0 XOR p0
    # And: p1 = c1 XOR k = c1 XOR c0 XOR p0
    
    # Extract the keystream from the known plaintext region
    keystream = bytes(c0[i] ^ p0[i] for i in range(len(p0)))
    
    # Use the keystream to decrypt message 1 at the target offset
    target_offset = target['offset']
    target_length = target['length']
    
    plaintext_bytes = bytes(
        c1[target_offset + i] ^ keystream[i]
        for i in range(target_length)
    )
    
    plaintext_hex = plaintext_bytes.hex()
    
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()