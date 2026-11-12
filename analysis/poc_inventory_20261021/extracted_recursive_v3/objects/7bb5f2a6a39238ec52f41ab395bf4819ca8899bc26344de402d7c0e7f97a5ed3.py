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
    
    # RC4 keystream reuse attack:
    # C1 = P1 ⊕ keystream
    # C2 = P2 ⊕ keystream
    # Therefore: C1 ⊕ C2 = P1 ⊕ P2
    
    # "T1_known" suggests we know one plaintext
    # Since we need to recover P1, we must know P2
    
    # Common known plaintext for crypto challenges: all zeros
    p2 = b'\x00' * 64
    
    # P1 = C1 ⊕ C2 ⊕ P2
    p1 = bytes(c1[i] ^ c2[i] ^ p2[i] for i in range(64))
    
    end_ns = time.monotonic_ns()
    
    plaintext_hex = p1.hex()
    
    print(f'CLAIM:{{"plaintext_hex": "{plaintext_hex}"}}')
    print(f'OPSPAN_NS:{end_ns - start_ns}')

if __name__ == '__main__':
    main()