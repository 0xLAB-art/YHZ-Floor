import json

with open('ciphertext') as f:
    ct = ''.join(f.read().split())

# The cipher: each byte of plaintext is split into n-bit chunks,
# key byte also split into n-bit chunks, XORed per chunk, then reassembled.
# Since XOR is its own inverse and chunk boundaries are preserved,
# decryption is just XOR of each byte with the key byte.

# Brute force single-byte keys (n must be < 8, but XOR works regardless)
for key_byte in range(256):
    flag = ''.join(chr((ord(c) ^ key_byte)) for c in ct)
    if flag.startswith('flag{'):
        print(flag)
        break
else:
    # Try multi-byte keys via known prefix
    for klen in range(1, 9):
        for key in range(256 ** klen):
            key_bytes = [(key >> (8 * (klen - 1 - i))) & 0xff for i in range(klen)]
            flag = ''.join(chr((ord(ct[i]) ^ key_bytes[i % klen])) for i in range(len(ct)))
            if flag.startswith('flag{'):
                print(flag)
                break
        else:
            continue
        break
