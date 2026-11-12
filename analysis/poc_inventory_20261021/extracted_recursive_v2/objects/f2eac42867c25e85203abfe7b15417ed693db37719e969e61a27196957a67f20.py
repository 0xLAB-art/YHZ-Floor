import sys
import json

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    ciphertext_1 = bytes.fromhex(data['ciphertext_1'])
    ciphertext_2 = bytes.fromhex(data['ciphertext_2'])
    plaintext_1 = bytes.fromhex(data['known_plaintext_1'])
    
    # ChaCha20 nonce reuse: C1 XOR P1 = keystream, keystream XOR C2 = P2
    keystream = xor_bytes(ciphertext_1, plaintext_1)
    plaintext_2 = xor_bytes(keystream, ciphertext_2)
    
    print(json.dumps({"plaintext_2": plaintext_2.hex()}))

if __name__ == '__main__':
    main()
