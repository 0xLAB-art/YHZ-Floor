import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    c1_hex = data['c1_hex']
    c2_hex = data['c2_hex']
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # c1 = p1 XOR keystream
    # c2 = p2 XOR keystream
    # Given p2 = all zeros (64 bytes)
    # c2 = 0 XOR keystream = keystream
    # Therefore: p1 = c1 XOR c2
    
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    
    result = {"plaintext2_hex": p1.hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()