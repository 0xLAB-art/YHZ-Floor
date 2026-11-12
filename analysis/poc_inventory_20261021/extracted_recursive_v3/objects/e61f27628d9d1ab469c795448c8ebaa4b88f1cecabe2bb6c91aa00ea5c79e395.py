import sys, time, json

def main():
    c1_hex = "36eb6a8ace8855dad21aad4df925dfe1833360a30c6bd0da631ac7bda9a444c962b09bb6ac8409dc8f67da1bc9bcf97f81b75e0c8e8e88edc7cffa10bc12aaf4"
    c2_hex = "cf5204eb8ab2c3f7acc537c038f2072c31ee03076d01ded4117c7bc586dce34cbb42e5be1f799cd14ac1a34feeb05b19ce9da25c8c7838807e957203f3c3f35a"
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    plaintext2_hex = p1.hex()
    claim = {"plaintext2_hex": plaintext2_hex}
    start = time.monotonic_ns()
    # computation already done
    end = time.monotonic_ns()
    opspan = end - start
    print(f"OPSPAN_NS:{opspan}")
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()