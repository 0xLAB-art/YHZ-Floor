import sys, json, binascii

def main():
    # Read all input (the provisioned JSON)
    data = sys.stdin.buffer.read()
    if not data:
        return
    # Decode to text and strip whitespace
    try:
        text = data.decode().strip()
    except Exception:
        return
    # Parse JSON
    try:
        obj = json.loads(text)
    except Exception:
        return
    c1_hex = obj.get('c1_hex')
    c2_hex = obj.get('c2_hex')
    if not c1_hex or not c2_hex:
        return
    # Convert hex to bytes
    c1 = binascii.unhexlify(c1_hex)
    c2 = binascii.unhexlify(c2_hex)
    # Recover plaintext by XORing the two ciphertexts (same keystream)
    plaintext = bytes(a ^ b for a, b in zip(c1, c2))
    pt_hex = binascii.hexlify(plaintext).decode()
    claim = {"plaintext_hex": pt_hex}
    # Output the claim line exactly as required
    sys.stdout.write(f"CLAIM:{json.dumps(claim, separators=(',', ':'))}\n")
    sys.stdout.flush()

if __name__ == '__main__':
    main()