import base64

# Read the output file
with open('output.txt', 'r') as f:
    lines = f.readlines()
    encrypted = lines[1].strip()

# The encryption algorithm shifts each character by its position
# To decrypt, we need to reverse this: subtract the position from each character

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
            # Reverse the encryption: chi_original = chi_encrypted - i
            dch = from_identity_map(chi - i)
        m += dch
    return m

decrypted = decrypt(encrypted)
flag = f"HTB{{{decrypted}}}"
print(flag)