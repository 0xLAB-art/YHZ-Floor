import base64

# Read and decode the encrypted flag from output.txt
with open('output.txt', 'r') as f:
    content = f.read()
    lines = content.strip().split('\n')
    encrypted_flag = lines[1]  # Second line contains the encrypted flag

# The encryption shifts each character by its position
# To decrypt: shift back by the position
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
            # Reverse the encryption: chi + i was applied, so subtract i
            dchi = chi - i
            dch = from_identity_map(dchi)
        m += dch
    return m

# Decrypt the flag
decrypted = decrypt(encrypted_flag)

# Wrap in HTB format
flag = f"HTB{{{decrypted}}}"

print(flag)