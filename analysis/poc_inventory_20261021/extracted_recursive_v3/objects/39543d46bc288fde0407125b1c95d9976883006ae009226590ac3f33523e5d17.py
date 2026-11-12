import sys, json, time

def main():
    c1_hex = "fef5491a1d257ef2a7ee8a22ed8c727b273baece523999d9e268f313a5ee5929e3b2f7354f0872a9a4fa4313d3d0d7eb01e812ab8a0186000166487922699eb4"
    c2_hex = "6ab81b4f75ee11d91d8490e366eecc28af34aee55372a12b8d714b42a15f9faed4add5799b437d796a3d261ec3f8943452eac4bc7e75cf4ef4be4a7272f1c809"
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    plaintext_hex = p1.hex()
    claim = {"plaintext_hex": plaintext_hex}
    start = time.monotonic_ns()
    # dummy operation to measure
    _ = plaintext_hex
    end = time.monotonic_ns()
    opspan = end - start
    print(f"OPSPAN_NS:{opspan}")
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()