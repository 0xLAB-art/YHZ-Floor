import sys

def main():
    with open('encrypted') as f:
        data = f.read().strip()
    buf = bytes.fromhex(data)
    out = bytearray()
    for i in range(0, len(buf), 2):
        if i + 1 < len(buf):
            out.append(buf[i] ^ buf[i + 1])
        else:
            out.append(buf[i])
    print(out.decode('latin1'))

if __name__ == '__main__':
    main()
