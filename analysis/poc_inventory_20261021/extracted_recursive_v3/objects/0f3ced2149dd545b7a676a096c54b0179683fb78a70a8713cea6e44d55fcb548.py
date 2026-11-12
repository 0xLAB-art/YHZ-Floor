import sys, json, binascii

def main():
    data = sys.stdin.read()
    if not data:
        return
    data = data.strip()
    if not data:
        return
    try:
        obj = json.loads(data)
    except Exception:
        return
    c1_hex = obj.get('c1_hex')
    c2_hex = obj.get('c2_hex')
    if not c1_hex or not c2_hex:
        return
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # Recover plaintext: c1 XOR c2 (keystream reuse)
    plaintext = bytes(a ^ b for a, b in zip(c1, c2))
    pt_hex = binascii.hexlify(plaintext).decode()
    claim = {"plaintext_hex": pt_hex}
    print(f"CLAIM:{json.dumps(claim, separators=(',', ':'))}")
    sys.stdout.flush()

if __name__ == '__main__':
    main()