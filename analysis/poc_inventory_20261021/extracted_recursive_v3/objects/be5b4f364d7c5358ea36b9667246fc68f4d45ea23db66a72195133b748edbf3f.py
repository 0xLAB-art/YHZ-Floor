import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    c1_hex = data['c1_hex']
    c2_hex = data['c2_hex']
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # ChaCha20 XOR property: c1 = p1 ⊕ keystream, c2 = p2 ⊕ keystream
    # Therefore: c1 ⊕ c2 = p1 ⊕ p2
    # Given p2 is all zeros: c1 ⊕ c2 = p1
    
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    
    result = {'plaintext2_hex': p1.hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()