import sys
import time

def main():
    c1_hex = "f6959823e005dcdb00b23a276ac816ff659d4bf1b9e33789e19aa014915f8987d011bf0b2af44b21b79b5685d827513ecfb5c07f43f39c560ddf8dcc61dd8a22"
    c2_hex = "ac1fd624821f190e291c47a2bcefb671c5c9a4322f899beceb804b2641dad22716bc8102985d438f514eab0ecb892d69c4c26d9e084fa3ce0708b5180b9d802c"
    c1 = bytes.fromhex(c1_hex)
    c2 = bytes.fromhex(c2_hex)
    p1 = bytes(a ^ b for a, b in zip(c1, c2))
    print(f"CLAIM:{{\"plaintext_hex\": \"{p1.hex()}\"}}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()