import sys
import json

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def bytes_to_hex(b):
    return b.hex()

def xor_bytes(b1, b2):
    return bytes(x ^ y for x, y in zip(b1, b2))

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertexts for message_index 0 and 1
    c0_data = None
    c1_data = None
    
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            c0_data = hex_to_bytes(ct['data'])
        elif ct['message_index'] == 1:
            c1_data = hex_to_bytes(ct['data'])
    
    # Find the known plaintext for message_index 0
    p0_data = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            p0_data = hex_to_bytes(kp['data'])
            p0_offset = kp['offset']
    
    # Extract the target region from message_index 1
    target_offset = target['offset']
    target_length = target['length']
    
    # Perform the attack: P1 = P0 ⊕ C0 ⊕ C1
    # We need to extract the relevant portions based on offsets
    
    # Since we have full ciphertexts and full known plaintext for message 0,
    # we can recover the keystream: K = P0 ⊕ C0
    keystream = xor_bytes(p0_data, c0_data)
    
    # Now decrypt message 1: P1 = C1 ⊕ K
    p1_data = xor_bytes(c1_data, keystream)
    
    # Extract the target portion
    target_plaintext = p1_data[target_offset:target_offset + target_length]
    
    # Output the result
    result = {
        "plaintext": bytes_to_hex(target_plaintext)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
