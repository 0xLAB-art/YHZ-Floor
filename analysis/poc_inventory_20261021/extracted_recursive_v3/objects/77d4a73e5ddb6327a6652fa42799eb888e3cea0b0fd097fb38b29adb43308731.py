import sys
import json

def main():
    c1_hex = "e3e5acede53358b4c8d39b3fae24310300933b60c1d8d94785b54985c1b3d691ab6926c3ab70051f50f8f2f6f22b11d6610e8d837effb9f4cc82676f3bc3ab6c"
    c2_hex = "155d4cb388a73268ec5bb0e25bc8af7f9fe6e8dcb51fba71a7e3a1072ab5836a3cf5c57a8744cab5378de45146437970ee59d74523dab00ba72921561f5ae8af"
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # Since c2 = keystream (encryption of all zeros)
    # and c1 = P1 XOR keystream
    # Then P1 = c1 XOR c2
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    
    claim = {"plaintext2_hex": p1.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()