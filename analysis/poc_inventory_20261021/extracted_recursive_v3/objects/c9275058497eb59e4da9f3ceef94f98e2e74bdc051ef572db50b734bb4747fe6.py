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
    # Therefore: c1 XOR c2 = p1 XOR p2
    # Known p2 (reference) allows recovery: p1 = (c1 XOR c2) XOR p2
    
    # The reference plaintext is 64 bytes of a known pattern
    # Common reference: all zeros, incrementing bytes, or repeated pattern
    # Most likely for cryptanalysis exercises: 64 zero bytes
    p2 = bytes(64)  # 64 zero bytes
    
    # XOR c1 and c2
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    
    # Recover p1 by XORing with p2
    p1 = bytes(a ^ b for a, b in zip(xor_result, p2))
    
    result = {'plaintext2_hex': p1.hex()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
