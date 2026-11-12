import sys
import json

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    c1_hex = "2f76c4beea3cb8d9464424be9bd3ece04055a48f59d24f549c1ba814b4e916d1a8e48becab930c6fb7c49611661771817aabe796d9c142be63a7c69bb9e00c3e"
    c2_hex = "8417b0c6a77ba8b4edbb28694ca7f5f8e81761753208bcdaf275fcef760fb479b4f20d2604e6a50560e095efd8bda0bd585d8d346e52a95ffeb3ab95036b5218"
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # Since c2 = keystream (encrypted zeros), P1 = c1 XOR c2
    p1 = xor_bytes(c1, c2)
    
    claim = {"plaintext2_hex": p1.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()