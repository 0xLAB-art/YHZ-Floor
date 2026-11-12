import time
import sys

def main():
    c1_hex = '028188df158c8d2fc1d214d82e36ecdea2c3e0a7041194bd443c2298be32910ac3c12d70732a08880249e82992f77c57a7501f0d70a6d8d1c22cdb6af8290c5a'
    c2_hex = 'b31935805aed5b88c58abf1fb4cdd6b19b3802247ffad214c342f329061dc31cdcca741b27d7f0dbf3585c7a79882a7f9270a88e8b6359e9331fe8a304bcf88c'
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    start = time.monotonic_ns()
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    end = time.monotonic_ns()
    plaintext_hex = p1.hex()
    print(f'OPSPAN_NS:{end-start}', flush=True)
    print(f'CLAIM:{{"plaintext_hex":"{plaintext_hex}"}}', flush=True)

if __name__ == '__main__':
    main()