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
    # Given p2 is the "64-byte reference", we assume it's known
    # p2 = "A" * 64 (common reference pattern)
    p2 = b'A' * 64
    
    # XOR c1 and c2 to get p1 XOR p2
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    
    # Recover p1: p1 = (c1 XOR c2) XOR p2
    p1 = bytes(a ^ b for a, b in zip(xor_result, p2))
    
    result = {
        'plaintext2_hex': p1.hex()
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()