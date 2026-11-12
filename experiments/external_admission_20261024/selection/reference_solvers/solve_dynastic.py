import sys
lines = open(sys.argv[1]).read().splitlines()
c = lines[1]
m = ""
for i, ch in enumerate(c):
    if not ch.isalpha():
        m += ch
    else:
        m += chr((ord(ch) - 0x41 - i) % 26 + 0x41)
print("HTB{" + m + "}")
