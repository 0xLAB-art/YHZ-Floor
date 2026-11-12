import sys

def main():
    c1_hex = "f8c92ad1d5a65ba6a15904b763d3b7a7901130fcca60bba90e564d5ea5658af9254cfa616de49efd581bc2f8e7b98a76cfc6c926535247541b543615e9ab2a2e"
    c2_hex = "2bcd10226028c89f1b416eb72fc3a54db1cfbe591e9aa37d2da387aa337ea5045af933887e863d79becd27e17262323e84ea24c0fb227d2f0bb3ae098322f9c4"
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    plaintext_hex = p1.hex()
    sys.stdout.write(f'CLAIM:{{"plaintext_hex":"{plaintext_hex}"}}\n')
    sys.stdout.flush()
    sys.stdout.write('OPSPAN_NS:0\n')
    sys.stdout.flush()

if __name__ == "__main__":
    main()