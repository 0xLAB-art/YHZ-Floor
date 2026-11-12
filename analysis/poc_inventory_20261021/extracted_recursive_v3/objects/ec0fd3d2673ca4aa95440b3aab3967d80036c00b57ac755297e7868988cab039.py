import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    public_input = instance['public_input']
    c1 = bytes.fromhex(public_input['c1_hex'])
    c2 = bytes.fromhex(public_input['c2_hex'])
    
    # XOR ciphertexts: C1 ⊕ C2 = P1 ⊕ P2
    xor_plaintexts = bytes(a ^ b for a, b in zip(c1, c2))
    
    # If P2 is known (likely all zeros or a standard message for "T1_known")
    # Try P2 = all zeros first
    p2_known = b'\x00' * 64
    p1 = bytes(a ^ b for a, b in zip(xor_plaintexts, p2_known))
    
    print(f'CLAIM:{{"plaintext2_hex": "{p1.hex()}"}}')

if __name__ == '__main__':
    main()