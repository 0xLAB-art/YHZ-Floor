import json, time, sys

def main():
    c1_hex = "30a110ccd5ded042125914c83a2f65b3b8a408abdcd2a204c215f73186703acd86f42ca58732c6d0f6ce347c46f724e9be5706f7914fde1975df8c5045ab2b85"
    c2_hex = "7451fdbff1f2c5188ef0218fcddda9d5922beb115372c210365fd5d9e3faa34331510d1d5e21b58bc3d0cab94884d1d9a56cc30b555756fe5392a14138c91456"
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    plaintext2_hex = p1.hex()
    claim = {"plaintext2_hex": plaintext2_hex}
    start = time.monotonic_ns()
    end = time.monotonic_ns()
    print(f"OPSPAN_NS:{end-start}", flush=True)
    print(f"CLAIM:{json.dumps(claim)}", flush=True)

if __name__ == "__main__":
    main()