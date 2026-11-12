import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse the instance
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertext for message 0 and message 1
    c0_data = None
    c1_data = None
    
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            c0_data = ct['data']
        elif ct['message_index'] == 1:
            c1_data = ct['data']
    
    # Find the known plaintext for message 0
    p0_data = None
    p0_offset = None
    
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            p0_data = kp['data']
            p0_offset = kp['offset']
    
    # Convert hex strings to bytes
    c0_bytes = bytes.fromhex(c0_data)
    c1_bytes = bytes.fromhex(c1_data)
    p0_bytes = bytes.fromhex(p0_data)
    
    # This is a stream cipher reuse attack (two-time pad)
    # If the same key is used: C0 = P0 XOR K, C1 = P1 XOR K
    # We know P0, C0, C1 and want P1
    # K = P0 XOR C0
    # P1 = C1 XOR K = C1 XOR (P0 XOR C0)
    
    # Extract the keystream from the known plaintext region
    # We have P0[p0_offset:p0_offset+len(p0_bytes)] and C0[p0_offset:p0_offset+len(p0_bytes)]
    
    # Recover the keystream at the known plaintext positions
    keystream_start = p0_offset
    keystream_length = len(p0_bytes)
    
    keystream = bytes([p0_bytes[i] ^ c0_bytes[p0_offset + i] for i in range(keystream_length)])
    
    # Now use this keystream to decrypt message 1 at the target location
    target_offset = target['offset']
    target_length = target['length']
    
    # Decrypt the target portion of message 1
    p1_target = bytes([c1_bytes[target_offset + i] ^ keystream[i] for i in range(target_length)])
    
    # Convert to hex
    result = p1_target.hex()
    
    # Output the result as JSON
    output = {"plaintext": result}
    print(json.dumps(output))

if __name__ == "__main__":
    main()