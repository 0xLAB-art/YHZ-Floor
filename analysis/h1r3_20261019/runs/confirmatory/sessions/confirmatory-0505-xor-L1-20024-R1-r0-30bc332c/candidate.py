import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertexts for message 0 and message 1
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
            break
    
    # Convert hex to bytes
    c0 = bytes.fromhex(c0_hex)
    c1 = bytes.fromhex(c1_hex)
    p0 = bytes.fromhex(p0_hex)
    
    # Extract the target portion
    offset = target['offset']
    length = target['length']
    
    # XOR attack: P1 = C1 ⊕ C0 ⊕ P0
    # Recover the key: K = C0 ⊕ P0
    # Then decrypt: P1 = C1 ⊕ K
    p1_bytes = []
    for i in range(offset, offset + length):
        # p1[i] = c1[i] ^ c0[i] ^ p0[i]
        p1_byte = c1[i] ^ c0[i] ^ p0[i]
        p1_bytes.append(p1_byte)
    
    p1 = bytes(p1_bytes)
    p1_hex = p1.hex()
    
    # Output result
    result = {"plaintext": p1_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
