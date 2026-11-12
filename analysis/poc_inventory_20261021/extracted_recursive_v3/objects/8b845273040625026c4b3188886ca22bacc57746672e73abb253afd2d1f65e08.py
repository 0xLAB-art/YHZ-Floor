import sys, json, binascii

def read_provision():
    # Read first non-empty line from stdin
    for line in sys.stdin:
        line = line.strip()
        if line:
            return line
    return ''

def main():
    line = read_provision()
    if not line:
        return
    try:
        obj = json.loads(line)
    except Exception as e:
        # If the whole stdin is a JSON without newline, fallback to reading all
        try:
            obj = json.loads(line + sys.stdin.read())
        except Exception:
            return
    c1_hex = obj.get('c1_hex')
    c2_hex = obj.get('c2_hex')
    if not c1_hex or not c2_hex:
        return
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # RC4 keystream reuse: ciphertext = plaintext XOR keystream
    # Since same keystream used, XOR of ciphertexts yields plaintext XOR 0s = plaintext
    plaintext = bytes(a ^ b for a, b in zip(c1, c2))
    pt_hex = binascii.hexlify(plaintext).decode()
    claim = {"plaintext_hex": pt_hex}
    print(f"CLAIM:{json.dumps(claim, separators=(',', ':'))}")
    sys.stdout.flush()

if __name__ == '__main__':
    main()