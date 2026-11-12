def to_identity_map(a):
    return ord(a) - 0x41

def from_identity_map(a):
    return chr(a % 26 + 0x41)

def decrypt(c):
    m = ''
    for i in range(len(c)):
        ch = c[i]
        if not ch.isalpha():
            dch = ch
        else:
            chi = to_identity_map(ch)
            dch = from_identity_map(chi - i)
        m += dch
    return m

with open('output.txt', 'r') as f:
    lines = f.readlines()
    ciphertext = lines[1].strip()

decrypted = decrypt(ciphertext)
flag = f"HTB{{{decrypted}}}"
print(flag)