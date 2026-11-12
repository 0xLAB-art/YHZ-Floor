import sys
import json
import base64

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    c1 = base64.b64decode(data['ciphertext_1'])
    c2 = base64.b64decode(data['ciphertext_2'])
    p1 = base64.b64decode(data['known_plaintext_1'])
    
    keystream = bytes(a ^ b for a, b in zip(c1, p1))
    p2 = bytes(a ^ b for a, b in zip(c2, keystream))
    
    result = {"plaintext_2": p2.hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()