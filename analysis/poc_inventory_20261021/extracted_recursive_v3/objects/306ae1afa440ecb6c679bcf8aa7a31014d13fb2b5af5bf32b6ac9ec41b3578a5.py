import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    c1_hex = data['c1_hex']
    c2_hex = data['c2_hex']
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # ChaCha20 with nonce reuse: c1 = p1 XOR keystream, c2 = p2 XOR keystream
    # XOR c1 and c2: c1 XOR c2 = p1 XOR p2
    # p2 is "a 64-byte reference" - assume it's 64 bytes of known plaintext
    # Common reference: all zeros, or a repeated pattern
    # Try p2 = 64 zero bytes
    
    p2_candidate = bytes(64)  # 64 zero bytes
    
    # c1 XOR c2 = p1 XOR p2
    # p1 = (c1 XOR c2) XOR p2
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    p1 = bytes(a ^ b for a, b in zip(xor_result, p2_candidate))
    
    result = {"plaintext2_hex": p1.hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
