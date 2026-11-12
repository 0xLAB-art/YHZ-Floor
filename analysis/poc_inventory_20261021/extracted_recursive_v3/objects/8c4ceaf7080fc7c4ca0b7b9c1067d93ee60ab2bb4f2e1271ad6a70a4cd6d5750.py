import sys, json, binascii

def main():
    # Read all input (the provisioned JSON)
    raw = sys.stdin.read()
    if not raw:
        return
    data = json.loads(raw.strip())
    c1_hex = data.get('c1_hex')
    c2_hex = data.get('c2_hex')
    if c1_hex is None or c2_hex is None:
        return
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # Recover plaintext: c1 = keystream XOR P1, c2 = keystream XOR 0 => c2 = keystream
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    p1_hex = binascii.hexlify(p1).decode()
    claim = {"plaintext2_hex": p1_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()