#!/usr/bin/env python3
import json
import sys

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    ct1 = bytes.fromhex(data['ciphertext_1'])
    ct2 = bytes.fromhex(data['ciphertext_2'])
    pt1 = bytes.fromhex(data['known_plaintext_1'])
    
    # ChaCha20 nonce reuse: C1 XOR P1 = keystream, then keystream XOR C2 = P2
    keystream = xor_bytes(ct1, pt1)
    pt2 = xor_bytes(keystream, ct2)
    
    result = {"plaintext_2": pt2.hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
