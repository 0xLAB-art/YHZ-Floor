import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    c1_hex = data['c1_hex']
    c2_hex = data['c2_hex']
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # c2 encrypts all zeros, so c2 = keystream XOR zeros = keystream
    keystream = c2
    
    # c1 = plaintext1 XOR keystream
    # plaintext1 = c1 XOR keystream = c1 XOR c2
    plaintext1 = bytes(a ^ b for a, b in zip(c1, c2))
    
    result = {
        "plaintext2_hex": plaintext1.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()