import json
import sys

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertext for message_index 0
    c0_data = None
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            c0_data = hex_to_bytes(ct['data'])
            break
    
    # Find the ciphertext for message_index 1
    c1_data = None
    for ct in ciphertexts:
        if ct['message_index'] == 1:
            c1_data = hex_to_bytes(ct['data'])
            break
    
    # Find the known plaintext for message_index 0
    p0_data = None
    p0_offset = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            p0_data = hex_to_bytes(kp['data'])
            p0_offset = kp['offset']
            break
    
    # This is a stream cipher reuse attack
    # C0 = P0 XOR K
    # C1 = P1 XOR K
    # Where K is the keystream
    
    # From known P0 and C0, we can recover the keystream K
    # K = P0 XOR C0
    
    # Extract the relevant portion of C0 that corresponds to P0
    c0_segment = c0_data[p0_offset:p0_offset + len(p0_data)]
    
    # Recover keystream for this segment
    keystream = xor_bytes(p0_data, c0_segment)
    
    # Now use the keystream to decrypt C1
    # P1 = C1 XOR K
    
    # Extract the target portion from C1
    target_offset = target['offset']
    target_length = target['length']
    c1_segment = c1_data[target_offset:target_offset + target_length]
    
    # Decrypt using the keystream
    # The keystream offset for message 1 should align with message 0
    # Assuming both messages use the same keystream starting at the same position
    keystream_segment = keystream[target_offset:target_offset + target_length]
    
    p1_segment = xor_bytes(c1_segment, keystream_segment)
    
    result = {
        "plaintext": bytes_to_hex(p1_segment)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
