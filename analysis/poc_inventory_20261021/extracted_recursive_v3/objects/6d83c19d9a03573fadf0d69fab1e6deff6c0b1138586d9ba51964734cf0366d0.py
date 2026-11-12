import sys
import json
import time

def main():
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    public_input = instance['public_input']
    c1_hex = public_input['c1_hex']
    c2_hex = public_input['c2_hex']
    
    # Convert to bytes
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    start_ns = time.monotonic_ns()
    
    # RC4 keystream reuse: C1 = P1 ⊕ K, C2 = P2 ⊕ K
    # C1 ⊕ C2 = P1 ⊕ P2
    # If P2 is known, then P1 = (C1 ⊕ C2) ⊕ P2
    
    # Assume P2 is all zeros (common in crypto challenges)
    p2 = b'\x00' * 64
    p1 = bytes(c1[i] ^ c2[i] ^ p2[i] for i in range(64))
    
    end_ns = time.monotonic_ns()
    
    plaintext_hex = p1.hex()
    
    print(f'CLAIM:{{"plaintext_hex": "{plaintext_hex}"}}')
    print(f'OPSPAN_NS:{end_ns - start_ns}')

if __name__ == '__main__':
    main()