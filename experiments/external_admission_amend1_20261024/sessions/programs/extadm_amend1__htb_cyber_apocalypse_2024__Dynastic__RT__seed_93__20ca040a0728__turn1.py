import base64

# Read the encrypted flag from output.txt
with open('output.txt', 'r') as f:
    lines = f.readlines()
    encrypted = lines[1].strip()

# Understand the encryption:
# For each character at position i:
#   - If not alpha: keep as-is
#   - If alpha: chi = ord(ch) - 0x41, then ech = chr((chi + i) % 26 + 0x41)
# To decrypt:
#   - If not alpha: keep as-is
#   - If alpha: ech_i = ord(ech) - 0x41, then chi = (ech_i - i) % 26, ch = chr(chi + 0x41)

def decrypt(c):
    m = ''
    for i in range(len(c)):
        ech = c[i]
        if not ech.isalpha():
            m += ech
        else:
            ech_i = ord(ech) - 0x41
            chi = (ech_i - i) % 26
            ch = chr(chi + 0x41)
            m += ch
    return m

decrypted = decrypt(encrypted)
flag = f"HTB{{{decrypted}}}"
print(flag)