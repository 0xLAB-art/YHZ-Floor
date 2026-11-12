import time, sys, json

def main():
    start = time.monotonic_ns()
    c1_hex = "acab44b48570443b4a0d357aedd526a5f47b4e9b2db560a065979a9f643a61ae740dfd9b4759d887da7ca700056e8637ea13610fb8f061d1ac79329508f71f6a"
    c2_hex = "1f877f4d204bb37ca37b1e48180371ceee30d5c35b38b71ad679e836d0983005a30f232fff85300c88d848bd4eda030215ed73acac4076736c0e6ec0ebce333f"
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    plaintext_hex = p1.hex()
    claim = {"plaintext2_hex": plaintext_hex}
    end = time.monotonic_ns()
    print(f"OPSPAN_NS:{end - start}")
    sys.stdout.flush()
    print("CLAIM:" + json.dumps(claim))
    sys.stdout.flush()

if __name__ == "__main__":
    main()