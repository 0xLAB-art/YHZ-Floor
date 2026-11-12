import sys, json, time

def main():
    c1_hex = "b86f9550877ef6804c141c334d8d303087c997d83f7c3b8e1e3f789a65958de286cec4163c83a58712855f6a38bb1297294d18c8062168f3c7c36a1acd8824f4"
    c2_hex = "cb71ca46bc310ddd3bf5bbae672fd4be121bc0cea2e52f8f0b85791a1ef71d937c802ed2b454cd683195b1753fa4e6b8a655e6e326f13382736c084e8ff92ea6"
    start = time.monotonic_ns()
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    plaintext2_hex = p1.hex()
    end = time.monotonic_ns()
    claim = {"plaintext2_hex": plaintext2_hex}
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()
    sys.stdout.write(f"OPSPAN_NS:{end-start}\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()