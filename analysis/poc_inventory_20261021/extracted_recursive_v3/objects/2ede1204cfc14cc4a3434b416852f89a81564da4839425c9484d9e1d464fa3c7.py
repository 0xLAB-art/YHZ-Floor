import sys, json, binascii

def main():
    # Read provisioned JSON from stdin (single line)
    line = sys.stdin.readline()
    if not line:
        return
    data = json.loads(line)
    c1_hex = data.get('c1_hex')
    c2_hex = data.get('c2_hex')
    if c1_hex is None or c2_hex is None:
        return
    # Convert to bytes
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # XOR to recover plaintext (since c2 is keystream of zeros)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    p1_hex = binascii.hexlify(p1).decode()
    # Output claim
    claim = {"plaintext2_hex": p1_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()