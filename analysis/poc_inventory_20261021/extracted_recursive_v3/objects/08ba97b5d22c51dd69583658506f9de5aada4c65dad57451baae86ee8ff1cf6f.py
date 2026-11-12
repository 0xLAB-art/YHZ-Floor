import sys
import json
import time

def main():
    c1_hex = "f5eb01715d21d5515e77b9b0e757cf5375890008c9333719e0f03eedb7673abe4947ddf382e5ebe52b31b21fbe92fede145c6b8b8892bbf783cb89a2f2ca51e4"
    c2_hex = "37ef4966f9dfa0cb555b5bf53f748f2df7e638f22a6bb8a391313d16c643036f0414dce4b036edbb6fe77794eca29640a8da4a9d27d9150a043213cb9aa6dda6"
    
    start = time.monotonic_ns()
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    plaintext_hex = p1.hex()
    end = time.monotonic_ns()
    
    print(f"OPSPAN_NS:{end - start}")
    print(f"CLAIM:{{\"plaintext_hex\": \"{plaintext_hex}\"}}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()