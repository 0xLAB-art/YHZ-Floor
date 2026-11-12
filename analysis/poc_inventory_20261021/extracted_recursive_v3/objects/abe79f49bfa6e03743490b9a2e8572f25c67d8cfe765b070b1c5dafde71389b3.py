import sys

def main():
    c1_hex = "04adb5fda5764d5491df33b097b7b0620c149ddc3f46791dd179efb45702f8a6b1041cdf731f7863f89c3e456f3627d6cc2d1b5fc6da6b0f5f1b8bb05685cae1"
    c2_hex = "7f168603d00cad7eb2b806a021b9499ac34edc14ba10d5db27af20af91a1baaa99105456dae0162addfdeed9269f47fd03bcc4d2bdc2437c1003e7950f423bd6"
    
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    
    # Since c2 = keystream (encryption of all zeros)
    # And c1 = P1 XOR keystream
    # Therefore P1 = c1 XOR c2
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    
    print(f'CLAIM:{{"plaintext2_hex": "{p1.hex()}"}}')
    sys.stdout.flush()

if __name__ == "__main__":
    main()