import sys

def main():
    data = open('encrypted', 'rb').read().strip()
    buf = bytes.fromhex(data.decode('ascii'))
    out = bytearray()
    for i, b in enumerate(buf):
        out.append(b ^ (i & 0xFF))
    print(out.decode('ascii', errors='replace'))

if __name__ == '__main__':
    main()