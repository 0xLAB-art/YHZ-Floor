import sys, time

def main():
    c1 = bytes.fromhex("1fb8f9d0c91867267a7db8db31a386d784b2faa49cbfcd3b32814618f307ee9b265169e528c3e40920deb878fe96bd5d1f7226592c04e3d38bb3e01ebdbdd6ef")
    c2 = bytes.fromhex("17178d4e7ad55bea9a3c5d57a802ac3f4ec58657bfdd437ab8aa0c7057cb97204ef2ca141bb8330164fb2d26dcbd0254e5aebbe2c1ebc0cb5c386a6313db5231")
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    start = time.monotonic_ns()
    # measurement around the computation (already done)
    end = time.monotonic_ns()
    span = end - start
    sys.stdout.write(f"CLAIM:{{\"plaintext_hex\":\"{p1.hex()}\"}}\n")
    if span:
        sys.stdout.write(f"OPSPAN_NS:{span}\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()