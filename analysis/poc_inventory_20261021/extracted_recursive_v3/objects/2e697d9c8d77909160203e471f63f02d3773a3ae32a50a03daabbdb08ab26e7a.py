import sys, time, json

def main():
    c1_hex = "a3efaa69b8717a6ea0ef29608374cbf7526cf276b7af419f01d5552851bbb62f50d35beee003aeb72dde7a63270ea00cb680da1b2575317e55e51e79116ad7eb"
    c2_hex = "9354632ef6b8af13c376112e2adac9a75ab2ea171ff2d6707d212312094a7bf8e4a6cced5bf816f5754ec1ff4ce4d0b6c9366aab6aa5243a0714bb8680c460b0"
    b1 = bytes.fromhex(c1_hex)
    b2 = bytes.fromhex(c2_hex)
    start = time.monotonic_ns()
    p = bytes(x ^ y for x, y in zip(b1, b2))
    end = time.monotonic_ns()
    plaintext_hex = p.hex()
    claim = {"plaintext_hex": plaintext_hex}
    print(f"OPSPAN_NS:{end - start}")
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()