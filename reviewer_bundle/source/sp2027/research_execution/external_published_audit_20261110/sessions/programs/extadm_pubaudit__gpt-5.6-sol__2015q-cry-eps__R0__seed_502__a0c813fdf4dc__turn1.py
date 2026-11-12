def main():
    filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
    with open(filename, "r", encoding="ascii") as f:
        bits = "".join(f.read().split())

    if not bits or len(bits) % 8 != 0 or any(bit not in "01" for bit in bits):
        raise ValueError("Invalid binary data")

    plaintext = bytes(
        int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)
    ).decode("utf-8")
    print(plaintext)


if __name__ == "__main__":
    main()
