import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    target = instance['target']
    ciphertexts = instance['ciphertexts']
    known_plaintexts = instance['known_plaintexts']
    
    # Find the ciphertexts and known plaintext
    c0_data = None
    c1_data = None
    p0_data = None
    
    for ct in ciphertexts:
        if ct['message_index'] == 0:
            c0_data = ct['data']
        elif ct['message_index'] == 1:
            c1_data = ct['data']
    
    for kp in known_plaintexts:
        if kp['message_index'] == 0:
            p0_data = kp['data']
    
    # Convert hex strings to bytes
    c0 = bytes.fromhex(c0_data)
    c1 = bytes.fromhex(c1_data)
    p0 = bytes.fromhex(p0_data)
    
    # Extract the target portion
    offset = target['offset']
    length = target['length']
    
    # XOR attack: P1 = C0 ⊕ C1 ⊕ P0
    p1_bytes = []
    for i in range(offset, offset + length):
        p1_byte = c0[i] ^ c1[i] ^ p0[i]
        p1_bytes.append(p1_byte)
    
    # Convert to hex
    p1_hex = bytes(p1_bytes).hex()
    
    # Output result
    result = {"plaintext": p1_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
