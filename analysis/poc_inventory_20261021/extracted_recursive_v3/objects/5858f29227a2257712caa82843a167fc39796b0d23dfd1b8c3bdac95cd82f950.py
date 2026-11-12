import sys
import json
import time

def main():
    c1_hex = "30683793c0e03cb258f91b20164b4e1f4ae3b26f65e0f431f1400e5e5dd157faccc9543b80aa10058d784809c158d32697dcbce09ed945524f1667c1462a1d7a"
    c2_hex = "20600189d212fa1c6aa67b57b7b92554878d17e7a311b7bdbe12bde04602abca293a8431eb1365f53c3acd960684a1a04386117b2ea7a55aff479812e5bcef26"
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # ChaCha20 with same key and nonce: c1 = P1 ^ keystream, c2 = 0 ^ keystream = keystream
    # So P1 = c1 ^ c2
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    
    claim = {"plaintext2_hex": p1.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()