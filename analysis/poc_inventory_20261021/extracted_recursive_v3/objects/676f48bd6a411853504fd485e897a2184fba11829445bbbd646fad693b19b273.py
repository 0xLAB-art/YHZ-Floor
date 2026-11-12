import sys
import json

def main():
    c1_hex = "9e13ab81b62cbf041824b1476afca16bd5b0c7abbc50df51f7e9577ca026f64819ec4558d310440cf387eec193afedf84061e1c4e5282969ef3c2f2aaf671936"
    c2_hex = "e70f6833ce14ac713b8364460bb685e704f9884518bfc639d5d7bf6313d454a85c09d61aa8c863d96acd6d5f26f6409c39037d7db618ce1fa06e3c463f5317d8"
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # keystream = c2 (since plaintext is all zeros)
    # P1 = c1 XOR keystream = c1 XOR c2
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    
    plaintext_hex = p1.hex()
    
    # Output claim
    claim = {"plaintext_hex": plaintext_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()