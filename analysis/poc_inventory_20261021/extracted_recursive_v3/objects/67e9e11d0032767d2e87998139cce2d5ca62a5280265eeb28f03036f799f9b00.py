import sys, json, binascii

def main():
    data = sys.stdin.read()
    if not data:
        return
    obj = json.loads(data)
    c1 = binascii.unhexlify(obj['c1_hex'])
    c2 = binascii.unhexlify(obj['c2_hex'])
    # XOR
    plaintext = bytes(a ^ b for a, b in zip(c1, c2))
    pt_hex = binascii.hexlify(plaintext).decode()
    claim = {"plaintext_hex": pt_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()