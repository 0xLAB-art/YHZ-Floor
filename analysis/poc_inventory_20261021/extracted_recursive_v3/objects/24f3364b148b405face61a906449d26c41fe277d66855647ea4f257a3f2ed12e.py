import sys
import json

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(byte_data):
    return byte_data.hex()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertexts for messages 0 and 1
    c0_hex = None
    c1_hex = None
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            c0_hex = ct['data']
        elif ct['message_index'] == 1:
            c1_hex = ct['data']
    
    # Find the known plaintext for message 0
    p0_hex = None
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            p0_hex = kp['data']
    
    # Convert to bytes
    c0 = hex_to_bytes(c0_hex)
    c1 = hex_to_bytes(c1_hex)
    p0 = hex_to_bytes(p0_hex)
    
    # Extract the required portion based on target
    offset = target['offset']
    length = target['length']
    
    # Recover the key from c0 and p0
    # K = C0 ⊕ P0
    key = xor_bytes(c0, p0)
    
    # Decrypt message 1 using the recovered key
    # P1 = C1 ⊕ K
    p1 = xor_bytes(c1, key)
    
    # Extract the target portion
    plaintext_bytes = p1[offset:offset + length]
    plaintext_hex = bytes_to_hex(plaintext_bytes)
    
    # Output result
    result = {"plaintext": plaintext_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()