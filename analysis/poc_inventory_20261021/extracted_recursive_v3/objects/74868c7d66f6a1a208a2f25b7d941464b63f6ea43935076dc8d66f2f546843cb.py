import sys, json

def main():
    c1_hex = "ffc14c79afd96a16a22e48b58dbffbd267d3e47697eaebb453b6bdc7f21b7e0c6190c7a324b8b642318f92e9351bff249f71a76b17c331791172f7fecf7878f1"
    c2_hex = "26bec107cbcca88205208d6e35674ce8b28fc97cc7ffcb955fdff370d63e3ed869180d3e6879f3b67046cd9876a3059c0b05745e900048da2f5e81f77f839f21"
    b1 = bytes.fromhex(c1_hex)
    b2 = bytes.fromhex(c2_hex)
    p = bytes(a ^ b for a, b in zip(b1, b2))
    claim = {"plaintext_hex": p.hex()}
    print("CLAIM:" + json.dumps(claim))
    # OPSPAN_NS:0

if __name__ == "__main__":
    main()