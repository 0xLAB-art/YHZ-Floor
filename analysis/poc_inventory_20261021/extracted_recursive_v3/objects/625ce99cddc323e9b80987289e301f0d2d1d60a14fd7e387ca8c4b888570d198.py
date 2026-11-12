import sys
import json

def main():
    c1_hex = "536a0736144cfca6afc0b8b1bc3cfedf025e62632fb2accdfcee1d30a7d62c9c248478b325de1490f449995f291f7bf7df2e7ec7ef75f69587bd734d14a04048"
    c2_hex = "c82d99af18e5cff7b007bc0cd27ff8276bcb53432beff248e7bbfe8a9474eab4f62794f6300a2d0986622c1ddcc9ae5aad3ba32d7a53c894559ef5a041819b52"
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # Since c2 = keystream (encrypted zeros), P1 = c1 XOR c2
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    
    claim = {"plaintext2_hex": p1.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()