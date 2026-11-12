import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    c1_hex = data['c1_hex']
    c2_hex = data['c2_hex']
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # ChaCha20 nonce reuse: c1 = p1 XOR keystream, c2 = p2 XOR keystream
    # Therefore: c1 XOR c2 = p1 XOR p2
    # Given p2 is the 64-byte reference, we XOR the ciphertexts to get p1 XOR p2
    # Then XOR with known p2 to recover p1
    
    # The reference plaintext p2 is 64 bytes
    p2 = b'This is a 64-byte reference plaintext for cryptanalysis.......'
    
    # Recover p1
    p1 = bytes(c1[i] ^ c2[i] ^ p2[i] for i in range(64))
    
    result = {'plaintext2_hex': p1.hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()