import sys, time, json

def main():
    c1_hex = "764362263b40746ae5301ddbbd843f9cb58cfe37c52ffd5b1db1b62f05393af541c0b69d0f2ed1d7df122f5030b4d5d0b454a9ce334c66e8d4b22f886d4122a1"
    c2_hex = "fa6fb0564a866bef011e36c94bbd63eb7469edb7df8ff89bcda06476a6d201fcd4b802207087093bbc1c68b4b943e84e5cb4dce2d47ec32704f230cfc4d95abe"
    start = time.monotonic_ns()
    b1 = bytes.fromhex(c1_hex)
    b2 = bytes.fromhex(c2_hex)
    p = bytes(x ^ y for x, y in zip(b1, b2))
    p_hex = p.hex()
    end = time.monotonic_ns()
    print(f"OPSPAN_NS:{end - start}")
    sys.stdout.flush()
    claim = {"plaintext_hex": p_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()