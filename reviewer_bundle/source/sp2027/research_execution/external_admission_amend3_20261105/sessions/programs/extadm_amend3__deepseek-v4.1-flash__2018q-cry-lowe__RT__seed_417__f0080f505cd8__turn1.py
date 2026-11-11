import base64
import math

def main():
    with open("pubkey.pem", "rb") as f:
        pem = f.read()
    n = None
    for line in pem.split(b"\n"):
        line = line.strip()
        if line.startswith(b"-----"):
            continue
        n = int(line, 16)
    with open("key.enc", "rb") as f:
        y = int(f.read().strip(), 10)
    with open("file.enc", "rb") as f:
        c = base64.b64decode(f.read().strip())
    k = round(n ** (1/3))
    while k**3 < n:
        k += 1
    assert k**3 == n + y
    y_bytes = k.to_bytes(192, "big")
    flag = bytes(a ^ b for a, b in zip(y_bytes, c))
    print(flag.decode())

if __name__ == "__main__":
    main()