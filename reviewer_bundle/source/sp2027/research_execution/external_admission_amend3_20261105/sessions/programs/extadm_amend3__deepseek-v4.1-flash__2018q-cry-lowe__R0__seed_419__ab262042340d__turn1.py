import base64
import math
import sys

def main():
    with open("pubkey.pem") as f:
        pem = f.read()
    b64 = "".join(line.strip() for line in pem.splitlines() if line.strip() and not line.startswith("-----"))
    der = base64.b64decode(b64)
    # parse SubjectPublicKeyInfo to extract modulus N
    idx = der.index(0x03)
    bitstring = der[idx:]
    unused = bitstring[0]
    n = int.from_bytes(bitstring[1+unused:], "big")
    e = 3

    with open("key.enc") as f:
        y = int(f.read().strip())
    with open("file.enc") as f:
        c_b64 = f.read().strip()
    c = base64.b64decode(c_b64)

    # Y + N is a perfect cube; root is K
    k = round((y + n) ** (1/3))
    while k**3 < y + n:
        k += 1
    while k**3 > y + n:
        k -= 1
    assert k**3 == y + n

    k_bytes = k.to_bytes((k.bit_length() + 7) // 8, "big")
    # pad to 192 bytes (Y is 192 bytes long)
    k_bytes = k_bytes.rjust(192, b"\x00")

    flag = bytes(a ^ b for a, b in zip(c, k_bytes))
    print(flag.decode("utf-8", errors="replace"))

if __name__ == "__main__":
    main()
